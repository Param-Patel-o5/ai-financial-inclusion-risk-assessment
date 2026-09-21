"""
Exploratory Data Analysis and Data Verification Script.

Performs read-only exploratory analysis and data quality auditing on data/model_table.parquet:
1. Basic Overview (shape, default rate, thin file & cold start counts)
2. Missing Values Analysis (every column, flagging model features > 20% nulls)
3. Model Feature Column Definitions
4. Distribution & 3-Sigma Outliers for Numeric Model Features
5. Categorical Column Distributions
6. Target Pearson Correlations (sorted by absolute magnitude)
7. Thin File vs Thick File Segmentation Analysis
8. Audit Columns Check (Fairness / Protected Attributes: Gender, Family Status, Age Bands)

NOTE:
- Read-only: Does not modify or overwrite data/model_table.parquet.
- No matplotlib calls (print only).
- Uses pandas and numpy only.
"""

from pathlib import Path
import numpy as np
import pandas as pd


# Model feature columns to analyze (excluding AUDIT-only features)
NUMERIC_MODEL_FEATURES = [
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "credit_income_ratio",
    "annuity_income_ratio",
    "employment_years",
    "late_payment_share",
    "mean_days_late",
    "max_days_late",
    "underpayment_share",
    "installments_count",
    "prev_applications_count",
    "prev_refused_count",
    "prev_refusal_rate",
    "mobile_bill_consistency",
    "thin_file",
]

CATEGORICAL_MODEL_FEATURES = [
    "NAME_EDUCATION_TYPE",
    "NAME_INCOME_TYPE",
    "NAME_HOUSING_TYPE",
]

ALL_MODEL_FEATURES = NUMERIC_MODEL_FEATURES + CATEGORICAL_MODEL_FEATURES

# Protected / Audit-Only attributes (tracked for fair lending auditing, not model inputs)
AUDIT_FEATURES = [
    "CODE_GENDER",
    "NAME_FAMILY_STATUS",
    "age_years",
]


def find_parquet_file() -> Path:
    """Locate data/model_table.parquet across common workspace relative paths."""
    base_dir = Path(__file__).resolve().parent.parent
    candidates = [
        base_dir / "data" / "model_table.parquet",
        base_dir / "Data" / "model_table.parquet",
        Path("data/model_table.parquet"),
        Path("Data/model_table.parquet"),
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    raise FileNotFoundError(
        "Could not find model_table.parquet in data/ or Data/. "
        "Please build the model table first using ml/build_features.py."
    )


def run_eda():
    """Execute complete EDA and data inspection pipeline."""
    parquet_path = find_parquet_file()
    print("=" * 80)
    print(f"LOADING PARQUET DATASET FROM: {parquet_path}")
    print("=" * 80)
    df = pd.read_parquet(parquet_path)

    # -------------------------------------------------------------------------
    # 1. Basic Overview
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("1. BASIC OVERVIEW")
    print("=" * 80)
    total_rows, total_cols = df.shape
    print(f"Shape of dataset: {total_rows:,} rows x {total_cols} columns")

    default_rate = df["TARGET"].mean()
    default_count = int(df["TARGET"].sum())
    print(
        f"Default rate (mean of TARGET): {default_rate:.4f} "
        f"({default_rate * 100:.2f}% | {default_count:,} defaults)"
    )

    thin_count = int((df["thin_file"] == 1).sum())
    thin_pct = (thin_count / total_rows) * 100
    print(f"Count and percentage of thin_file == 1: {thin_count:,} ({thin_pct:.2f}%)")

    cold_start_mask = (df["thin_file"] == 1) & (df["installments_count"] == 0)
    cold_start_count = int(cold_start_mask.sum())
    cold_start_pct_total = (cold_start_count / total_rows) * 100
    cold_start_pct_thin = (cold_start_count / thin_count) * 100
    print(
        f"Count of thin_file == 1 with installments_count == 0 (truly cold start): "
        f"{cold_start_count:,} ({cold_start_pct_total:.2f}% of dataset, "
        f"{cold_start_pct_thin:.2f}% of thin_file)"
    )

    # -------------------------------------------------------------------------
    # 2. Missing Values Analysis
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("2. MISSING VALUES ANALYSIS")
    print("=" * 80)
    null_counts = df.isna().sum()
    null_pcts = (null_counts / total_rows) * 100
    null_summary = pd.DataFrame(
        {
            "Column": df.columns,
            "Null_Count": null_counts.values,
            "Null_Percentage": null_pcts.values,
        }
    )

    print("Count and percentage of nulls for every column (136 columns):")
    pd.set_option("display.max_rows", None)
    pd.set_option("display.width", 1000)
    print(
        null_summary.to_string(
            index=False,
            formatters={
                "Null_Count": lambda x: f"{x:7,d}",
                "Null_Percentage": lambda x: f"{x:6.2f}%",
            },
        )
    )
    pd.reset_option("display.max_rows")
    pd.reset_option("display.width")

    print("\n--- Model Feature Columns > 20% Nulls Check ---")
    flagged_model_features = []
    for col in ALL_MODEL_FEATURES:
        pct = (df[col].isna().sum() / total_rows) * 100
        if pct > 20.0:
            flagged_model_features.append((col, pct))

    if flagged_model_features:
        print("FLAGGED MODEL FEATURES (> 20% missing):")
        for col, pct in flagged_model_features:
            print(f"  [!] {col}: {pct:.2f}% missing")
    else:
        print("No model feature columns exceed the 20% missing value threshold.")
        print(
            f"Highest missingness in model features: employment_years "
            f"({(df['employment_years'].isna().sum() / total_rows) * 100:.2f}%), "
            f"mobile_bill_consistency "
            f"({(df['mobile_bill_consistency'].isna().sum() / total_rows) * 100:.2f}%)."
        )

    # -------------------------------------------------------------------------
    # 3. Model Feature Columns List
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("3. MODEL FEATURE COLUMNS TO ANALYZE (NOT AUDIT COLUMNS)")
    print("=" * 80)
    print(f"Total model features defined: {len(ALL_MODEL_FEATURES)}")
    print(f"Numeric model features ({len(NUMERIC_MODEL_FEATURES)}):")
    for i, col in enumerate(NUMERIC_MODEL_FEATURES, 1):
        print(f"  {i:2d}. {col}")
    print(f"\nCategorical model features ({len(CATEGORICAL_MODEL_FEATURES)}):")
    for i, col in enumerate(CATEGORICAL_MODEL_FEATURES, 1):
        print(f"  {i:2d}. {col}")

    # -------------------------------------------------------------------------
    # 4. Distribution Check for Numeric Model Features
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("4. DISTRIBUTION CHECK & 3-SIGMA OUTLIERS (NUMERIC MODEL FEATURES)")
    print("=" * 80)
    dist_records = []
    for col in NUMERIC_MODEL_FEATURES:
        series = df[col].dropna()
        mean_val = series.mean()
        median_val = series.median()
        std_val = series.std()
        min_val = series.min()
        max_val = series.max()

        if std_val > 0:
            outlier_mask = (series < (mean_val - 3 * std_val)) | (
                series > (mean_val + 3 * std_val)
            )
            outlier_count = int(outlier_mask.sum())
            outlier_pct = (outlier_count / len(series)) * 100
        else:
            outlier_count = 0
            outlier_pct = 0.0

        dist_records.append(
            {
                "Feature": col,
                "Mean": mean_val,
                "Median": median_val,
                "Std": std_val,
                "Min": min_val,
                "Max": max_val,
                "Outliers (>3 Std)": outlier_count,
                "Outlier %": outlier_pct,
            }
        )

    df_dist = pd.DataFrame(dist_records)
    print(
        df_dist.to_string(
            index=False,
            formatters={
                "Mean": lambda x: f"{x:12.4f}",
                "Median": lambda x: f"{x:12.4f}",
                "Std": lambda x: f"{x:12.4f}",
                "Min": lambda x: f"{x:12.4f}",
                "Max": lambda x: f"{x:14.4f}",
                "Outliers (>3 Std)": lambda x: f"{x:7,d}",
                "Outlier %": lambda x: f"{x:6.2f}%",
            },
        )
    )

    # -------------------------------------------------------------------------
    # 5. Categorical Columns Analysis
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("5. CATEGORICAL COLUMNS VALUE COUNTS & PERCENTAGES")
    print("=" * 80)
    for cat_col in CATEGORICAL_MODEL_FEATURES:
        print(f"\n--- {cat_col} ---")
        counts = df[cat_col].value_counts(dropna=False)
        pcts = df[cat_col].value_counts(dropna=False, normalize=True) * 100
        cat_df = pd.DataFrame({"Count": counts, "Percentage (%)": pcts})
        print(
            cat_df.to_string(
                formatters={
                    "Count": lambda x: f"{x:8,d}",
                    "Percentage (%)": lambda x: f"{x:6.2f}%",
                }
            )
        )

    # -------------------------------------------------------------------------
    # 6. Target Correlation
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("6. TARGET CORRELATION (PEARSON CORRELATION WITH TARGET)")
    print("=" * 80)
    correlations = []
    target_series = df["TARGET"]
    for col in NUMERIC_MODEL_FEATURES:
        series = df[col]
        # Valid non-null mask for both series and target
        valid_mask = series.notna() & target_series.notna()
        r = float(np.corrcoef(series[valid_mask], target_series[valid_mask])[0, 1])
        correlations.append(
            {
                "Feature": col,
                "Pearson_Correlation": r,
                "Abs_Correlation": abs(r),
            }
        )

    df_corr = pd.DataFrame(correlations).sort_values(
        by="Abs_Correlation", ascending=False
    )
    print(
        df_corr.to_string(
            index=False,
            formatters={
                "Pearson_Correlation": lambda x: f"{x:+9.5f}",
                "Abs_Correlation": lambda x: f"{x:9.5f}",
            },
        )
    )

    # -------------------------------------------------------------------------
    # 7. Thin File Analysis
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("7. THIN FILE SEGMENTATION ANALYSIS")
    print("=" * 80)
    thin_grp = df.groupby("thin_file")
    print("Default rate for thin_file == 1 vs thin_file == 0:")
    for tf_val in [0, 1]:
        sub = df[df["thin_file"] == tf_val]
        label = "Thick File (thin_file == 0)" if tf_val == 0 else "Thin File (thin_file == 1)"
        rate = sub["TARGET"].mean()
        defaults = int(sub["TARGET"].sum())
        total = len(sub)
        print(
            f"  {label:28s}: Default Rate = {rate:.4f} ({rate * 100:.2f}%) "
            f"[{defaults:,} / {total:,} applicants]"
        )

    installment_features = [
        "late_payment_share",
        "mean_days_late",
        "max_days_late",
        "underpayment_share",
        "installments_count",
    ]
    print("\nMean of each installment feature for thin vs thick file:")
    thin_inst_means = (
        df.groupby("thin_file")[installment_features]
        .mean()
        .rename(index={0: "Thick File (0)", 1: "Thin File (1)"})
        .T
    )
    thin_inst_means["Difference (Thin - Thick)"] = (
        thin_inst_means["Thin File (1)"] - thin_inst_means["Thick File (0)"]
    )
    print(
        thin_inst_means.to_string(
            formatters={
                "Thick File (0)": lambda x: f"{x:12.4f}",
                "Thin File (1)": lambda x: f"{x:12.4f}",
                "Difference (Thin - Thick)": lambda x: f"{x:+12.4f}",
            }
        )
    )

    # -------------------------------------------------------------------------
    # 8. Audit Columns Check (Fair Lending / Demographic Monitoring)
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("8. AUDIT COLUMNS CHECK (FAIR LENDING / PROTECTED ATTRIBUTES)")
    print("=" * 80)
    for audit_cat in ["CODE_GENDER", "NAME_FAMILY_STATUS"]:
        print(f"\n--- Value Counts for {audit_cat} ---")
        counts = df[audit_cat].value_counts(dropna=False)
        pcts = df[audit_cat].value_counts(dropna=False, normalize=True) * 100
        audit_df = pd.DataFrame({"Count": counts, "Percentage (%)": pcts})
        print(
            audit_df.to_string(
                formatters={
                    "Count": lambda x: f"{x:8,d}",
                    "Percentage (%)": lambda x: f"{x:6.2f}%",
                }
            )
        )

    print("\n--- Age Distribution (age_years) ---")
    age_series = df["age_years"]
    print(f"Mean Age : {age_series.mean():.2f} years")
    print(f"Min Age  : {age_series.min():.0f} years")
    print(f"Max Age  : {age_series.max():.0f} years")
    print(f"Median   : {age_series.median():.0f} years")
    print(f"Std Dev  : {age_series.std():.2f} years")

    # Age bands: 18-25, 26-35, 36-50, 51+
    bins = [17, 25, 35, 50, 150]
    labels = ["18-25", "26-35", "36-50", "51+"]
    age_bands = pd.cut(age_series, bins=bins, labels=labels)

    band_counts = age_bands.value_counts(sort=False)
    band_pcts = age_bands.value_counts(sort=False, normalize=True) * 100
    df_age_bands = pd.DataFrame({"Count": band_counts, "Percentage (%)": band_pcts})
    print("\nCount and percentage per age band:")
    print(
        df_age_bands.to_string(
            formatters={
                "Count": lambda x: f"{x:8,d}",
                "Percentage (%)": lambda x: f"{x:6.2f}%",
            }
        )
    )
    print("\n" + "=" * 80)
    print("EDA & DATA INSPECTION COMPLETE (READ-ONLY)")
    print("=" * 80)


if __name__ == "__main__":
    run_eda()
