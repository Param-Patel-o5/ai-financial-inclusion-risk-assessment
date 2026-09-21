"""
Data preprocessing and feature engineering pipeline for Financial Inclusion Risk Assessment.

Merges 5 raw datasets into a unified model table saved as data/model_table.parquet:
- application_train.csv: Main application file containing TARGET.
- bureau.csv: Computes thin_file flag (1 if applicant has 0 bureau records, 0 otherwise).
- installments_payments.csv: Aggregates payment timeliness and completeness.
- previous_application.csv: Aggregates previous credit applications and refusal metrics.
- synthetic_alt_data.csv: Merges synthetic alternative data (mobile_bill_consistency).

================================================================================
AUDIT ONLY (Fair lending / Bias monitoring - DO NOT USE AS MODEL TRAINING FEATURES):
- CODE_GENDER
- NAME_FAMILY_STATUS
- age_years
================================================================================
"""

import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# ==============================================================================
# AUDIT ONLY FEATURES (Compliance & Fairness Auditing):
# Preserved exclusively for disparate impact / fairness analysis.
# MUST NOT be used as predictive model training features.
AUDIT_ONLY_COLUMNS = [
    "CODE_GENDER",
    "NAME_FAMILY_STATUS",
    "age_years",
]
# ==============================================================================


def find_data_file(base_dir: Path, relative_name: str) -> Path:
    """Find file in either data/raw or Data/raw."""
    candidates = [
        base_dir / "data" / "raw" / relative_name,
        base_dir / "Data" / "raw" / relative_name,
        Path("data/raw") / relative_name,
        Path("Data/raw") / relative_name,
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(
        f"Could not find {relative_name} in data/raw or Data/raw."
    )


def resolve_output_path(base_dir: Path) -> Path:
    """Resolve destination path for data/model_table.parquet."""
    candidates = [
        base_dir / "data",
        base_dir / "Data",
        Path("data"),
        Path("Data"),
    ]
    for p in candidates:
        if p.exists():
            return p / "model_table.parquet"

    out_dir = base_dir / "data"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / "model_table.parquet"


def build_model_table() -> pd.DataFrame:
    """
    Load raw datasets, apply transformations, perform left joins on SK_ID_CURR,
    and save the combined dataset to data/model_table.parquet.
    """
    start_time = time.time()
    base_dir = Path(__file__).resolve().parent.parent

    print("=" * 70)
    print("STARTING DATA MERGE & FEATURE ENGINEERING PIPELINE")
    print("=" * 70)

    # 1. Main File: application_train.csv
    app_path = find_data_file(base_dir, "application_train.csv")
    print(f"\n[1/5] Loading application_train from: {app_path}")
    df_main = pd.read_csv(app_path)
    print(f"      Loaded {len(df_main):,} rows, {df_main.shape[1]} columns.")

    # Transformations on application_train
    print("\nApplying transformations on application data:")
    # DAYS_EMPLOYED 365243 -> NaN, then employment_years = -DAYS_EMPLOYED/365
    print("  - Replacing DAYS_EMPLOYED == 365243 with NaN and computing employment_years")
    df_main["DAYS_EMPLOYED"] = df_main["DAYS_EMPLOYED"].replace(365243, np.nan)
    df_main["employment_years"] = -df_main["DAYS_EMPLOYED"] / 365.0

    # age_years = (-DAYS_BIRTH/365).astype(int)
    print("  - Computing age_years = (-DAYS_BIRTH / 365).astype(int)")
    df_main["age_years"] = (-df_main["DAYS_BIRTH"] / 365.0).astype(int)

    # credit_income_ratio = AMT_CREDIT / AMT_INCOME_TOTAL
    print("  - Computing credit_income_ratio = AMT_CREDIT / AMT_INCOME_TOTAL")
    df_main["credit_income_ratio"] = (
        df_main["AMT_CREDIT"] / df_main["AMT_INCOME_TOTAL"]
    )

    # annuity_income_ratio = AMT_ANNUITY / AMT_INCOME_TOTAL
    print("  - Computing annuity_income_ratio = AMT_ANNUITY / AMT_INCOME_TOTAL")
    df_main["annuity_income_ratio"] = (
        df_main["AMT_ANNUITY"] / df_main["AMT_INCOME_TOTAL"]
    )

    # 2. Bureau File: bureau.csv
    bureau_path = find_data_file(base_dir, "bureau.csv")
    print(f"\n[2/5] Processing bureau data from: {bureau_path}")
    bureau_ids = set(
        pd.read_csv(bureau_path, usecols=["SK_ID_CURR"])["SK_ID_CURR"].unique()
    )
    # thin_file flag: 1 if applicant has zero bureau records, 0 otherwise
    df_main["thin_file"] = (~df_main["SK_ID_CURR"].isin(bureau_ids)).astype(int)
    thin_count = int(df_main["thin_file"].sum())
    print(
        f"      Created thin_file flag: {thin_count:,} / {len(df_main):,} "
        f"({thin_count / len(df_main):.2%}) have zero bureau records."
    )

    # 3. Installments File: installments_payments.csv
    inst_path = find_data_file(base_dir, "installments_payments.csv")
    print(f"\n[3/5] Processing installments data from: {inst_path}")
    inst_cols = [
        "SK_ID_CURR",
        "DAYS_INSTALMENT",
        "DAYS_ENTRY_PAYMENT",
        "AMT_INSTALMENT",
        "AMT_PAYMENT",
    ]
    df_inst = pd.read_csv(inst_path, usecols=inst_cols)
    print(f"      Loaded {len(df_inst):,} installments rows.")

    # Installments logic:
    # days_late = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT clipped at 0
    days_late = (df_inst["DAYS_ENTRY_PAYMENT"] - df_inst["DAYS_INSTALMENT"]).clip(
        lower=0
    )
    # is_late = 1 if days_late > 0
    is_late = (days_late > 0).astype(int)
    # underpaid = 1 if AMT_PAYMENT < AMT_INSTALMENT
    underpaid = (df_inst["AMT_PAYMENT"] < df_inst["AMT_INSTALMENT"]).astype(int)

    df_inst["days_late"] = days_late
    df_inst["is_late"] = is_late
    df_inst["underpaid"] = underpaid

    print("      Aggregating installments metrics per SK_ID_CURR...")
    inst_agg = (
        df_inst.groupby("SK_ID_CURR")
        .agg(
            late_payment_share=("is_late", "mean"),
            mean_days_late=("days_late", "mean"),
            max_days_late=("days_late", "max"),
            underpayment_share=("underpaid", "mean"),
            installments_count=("SK_ID_CURR", "count"),
        )
        .reset_index()
    )
    del df_inst  # free memory

    # 4. Previous Applications File: previous_application.csv
    prev_path = find_data_file(base_dir, "previous_application.csv")
    print(f"\n[4/5] Processing previous applications from: {prev_path}")
    prev_cols = ["SK_ID_CURR", "NAME_CONTRACT_STATUS"]
    df_prev = pd.read_csv(prev_path, usecols=prev_cols)
    print(f"      Loaded {len(df_prev):,} previous application records.")

    df_prev["is_refused"] = (
        df_prev["NAME_CONTRACT_STATUS"] == "Refused"
    ).astype(int)

    print("      Aggregating previous applications metrics per SK_ID_CURR...")
    prev_agg = (
        df_prev.groupby("SK_ID_CURR")
        .agg(
            prev_applications_count=("NAME_CONTRACT_STATUS", "count"),
            prev_refused_count=("is_refused", "sum"),
        )
        .reset_index()
    )
    prev_agg["prev_refusal_rate"] = (
        prev_agg["prev_refused_count"] / prev_agg["prev_applications_count"]
    )
    del df_prev  # free memory

    # 5. Synthetic Alternative Data: synthetic_alt_data.csv
    syn_path = find_data_file(base_dir, "synthetic_alt_data.csv")
    print(f"\n[5/5] Processing synthetic alt data from: {syn_path}")
    df_syn = pd.read_csv(syn_path)
    print(f"      Loaded {len(df_syn):,} rows of synthetic data.")

    # Left Joins on SK_ID_CURR
    print("\nPerforming left joins on SK_ID_CURR:")
    # Installments join
    print("  - Merging installments aggregates...")
    df_main = df_main.merge(inst_agg, on="SK_ID_CURR", how="left")
    del inst_agg

    # Previous application join
    print("  - Merging previous application aggregates...")
    df_main = df_main.merge(prev_agg, on="SK_ID_CURR", how="left")
    del prev_agg

    # Synthetic alt data join
    print("  - Merging synthetic alt data...")
    df_main = df_main.merge(
        df_syn[["SK_ID_CURR", "mobile_bill_consistency"]],
        on="SK_ID_CURR",
        how="left",
    )
    del df_syn

    # Handle missing values as specified:
    # "All aggregated fields from installments and previous_application: fillna(0)"
    # "mobile_bill_consistency: leave NaN as is"
    inst_prev_agg_cols = [
        "late_payment_share",
        "mean_days_late",
        "max_days_late",
        "underpayment_share",
        "installments_count",
        "prev_applications_count",
        "prev_refused_count",
        "prev_refusal_rate",
    ]
    print(
        f"\nFilling missing values with 0 for {len(inst_prev_agg_cols)} aggregated fields..."
    )
    df_main[inst_prev_agg_cols] = df_main[inst_prev_agg_cols].fillna(0)

    # Save to Parquet using pyarrow
    output_path = resolve_output_path(base_dir)
    print(f"\nSaving model table to Parquet: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_main.to_parquet(output_path, engine="pyarrow", index=False)
    print("Parquet file saved successfully.")

    # Print summary statistics as requested:
    # "Print final shape, thin_file count, default rate, and null count per column at the end."
    print("\n" + "=" * 70)
    print("SUMMARY METRICS")
    print("=" * 70)
    print(f"Final shape: {df_main.shape[0]:,} rows x {df_main.shape[1]} columns")

    thin_count = int(df_main["thin_file"].sum())
    thin_pct = (thin_count / len(df_main)) * 100
    print(f"thin_file count: {thin_count:,} ({thin_pct:.2f}%)")

    if "TARGET" in df_main.columns:
        default_rate = float(df_main["TARGET"].mean())
        default_count = int(df_main["TARGET"].sum())
        print(
            f"Default rate: {default_rate:.4f} ({default_rate * 100:.2f}%, {default_count:,} / {len(df_main):,})"
        )

    print("\n--- AUDIT ONLY COLUMNS REMINDER ---")
    print(f"Audit Only features: {AUDIT_ONLY_COLUMNS}")
    print("Do not use these columns as model predictive features.")

    print("\n--- NULL COUNT PER COLUMN ---")
    null_counts = df_main.isna().sum()
    null_cols = null_counts[null_counts > 0]
    print(f"Total columns with missing values: {len(null_cols)} / {df_main.shape[1]}")
    pd.set_option("display.max_rows", None)
    print(null_counts)
    pd.reset_option("display.max_rows")

    elapsed = time.time() - start_time
    print(f"\nPipeline finished in {elapsed:.1f} seconds.")
    print("=" * 70)

    return df_main


if __name__ == "__main__":
    build_model_table()
