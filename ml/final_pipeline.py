"""
Final Production Machine Learning Pipeline for Financial Inclusion Risk Assessment.

Executes complete end-to-end workflow:
Step 0: Income type ablation (decides whether to drop NAME_INCOME_TYPE based on 0.003 AUC threshold).
Step 1: Train final LightGBM model (stratified 60/20/20, seed 42).
Step 2: Fit Isotonic Regression calibrator on validation set with 0.005 floor.
Step 3: Decile table on test set with equal bin sizes (pd.qcut rank method='first').
Step 4: Compute decision thresholds (bottom 60% approve, top 15% deny) and evaluate on test set.
Step 5: SHAP TreeExplainer analysis & quintile direction checks.
Step 6: Reason code selection with dedup rule (AMT_CREDIT vs credit_income_ratio loan_size group).
Step 7: Recreate demo pool (200 rows: 50 thin, 150 thick) with zero overlap assertion.
Step 8: Save all production artifacts.
Step 9: Update ml/feature_registry.yaml.
Step 10: Print final comprehensive summary.
"""

import json
import os
import pickle
import time
from pathlib import Path
import lightgbm as lgb
import numpy as np
import pandas as pd
import shap
import yaml
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Base 15 features (always included)
BASE_FEATURES = [
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
    "thin_file",
]

# Audit columns (never passed to model)
AUDIT_COLUMNS = [
    "CODE_GENDER",
    "NAME_FAMILY_STATUS",
    "age_years",
]

# 10 eligible reason code features in order of priority
ELIGIBLE_REASON_FEATURES = [
    "employment_years",
    "late_payment_share",
    "prev_refusal_rate",
    "installments_count",
    "underpayment_share",
    "mean_days_late",
    "AMT_CREDIT",
    "credit_income_ratio",
    "annuity_income_ratio",
    "thin_file",
]

# LightGBM exact parameters
LGBM_PARAMS = {
    "objective": "binary",
    "metric": "auc",
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 20,
    "class_weight": "balanced",
    "random_state": 42,
    "n_estimators": 1000,
    "early_stopping_rounds": 50,
    "verbose": -1,
}


def resolve_paths():
    """Resolve file system paths."""
    base_dir = Path(__file__).resolve().parent.parent

    data_dir = base_dir / "data"
    if not data_dir.exists() and (base_dir / "Data").exists():
        data_dir = base_dir / "Data"

    parquet_path = data_dir / "model_table.parquet"
    demo_pool_path = data_dir / "demo_pool.parquet"
    ml_dir = base_dir / "ml"
    encoders_dir = ml_dir / "encoders"
    encoders_dir.mkdir(parents=True, exist_ok=True)

    if not parquet_path.exists():
        raise FileNotFoundError(f"Missing {parquet_path}")

    return base_dir, data_dir, parquet_path, demo_pool_path, ml_dir, encoders_dir


def main():
    total_start = time.time()
    base_dir, data_dir, parquet_path, demo_pool_path, ml_dir, encoders_dir = resolve_paths()

    print("=" * 80)
    print("FINAL PRODUCTION ML PIPELINE (AUTOMATED ABLATION & DEPLOYMENT)")
    print("=" * 80)

    # -------------------------------------------------------------------------
    # STEP 0 — Income type ablation first
    # -------------------------------------------------------------------------
    print("\n[Step 0] Running Income Type Ablation...")
    df = pd.read_parquet(parquet_path)

    # Encode NAME_INCOME_TYPE
    le_income = LabelEncoder()
    df["NAME_INCOME_TYPE"] = le_income.fit_transform(df["NAME_INCOME_TYPE"].astype(str))

    # Stratified split 60/20/20 seed 42
    train_df, temp_df = train_test_split(
        df, test_size=0.40, random_state=42, stratify=df["TARGET"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=42, stratify=temp_df["TARGET"]
    )

    train_df = train_df.reset_index(drop=True)
    val_df = val_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    y_train = train_df["TARGET"]
    y_val = val_df["TARGET"]
    y_test = test_df["TARGET"]

    feats_16 = BASE_FEATURES + ["NAME_INCOME_TYPE"]
    feats_15 = BASE_FEATURES

    # Model A: 16 features (including NAME_INCOME_TYPE)
    clf_a = lgb.LGBMClassifier(**LGBM_PARAMS)
    clf_a.fit(train_df[feats_16], y_train, eval_set=[(val_df[feats_16], y_val)], eval_metric="auc")
    auc_a = roc_auc_score(y_test, clf_a.predict_proba(test_df[feats_16])[:, 1])

    # Model B: 15 features (excluding NAME_INCOME_TYPE)
    clf_b = lgb.LGBMClassifier(**LGBM_PARAMS)
    clf_b.fit(train_df[feats_15], y_train, eval_set=[(val_df[feats_15], y_val)], eval_metric="auc")
    auc_b = roc_auc_score(y_test, clf_b.predict_proba(test_df[feats_15])[:, 1])

    auc_diff = auc_a - auc_b
    print(f"  Model A (16 features with NAME_INCOME_TYPE)    Test AUC: {auc_a:.5f}")
    print(f"  Model B (15 features without NAME_INCOME_TYPE) Test AUC: {auc_b:.5f}")
    print(f"  AUC Difference (Model A - Model B)                     : {auc_diff:+.5f}")

    if auc_diff < 0.003:
        DROP_INCOME_TYPE = True
        FINAL_FEATURES = feats_15
        print("  Decision: DROP_INCOME_TYPE = True (AUC difference < 0.003 threshold). Proceeding with 15 features.")
    else:
        DROP_INCOME_TYPE = False
        FINAL_FEATURES = feats_16
        print("  Decision: DROP_INCOME_TYPE = False (AUC difference >= 0.003 threshold). Proceeding with 16 features.")

    # -------------------------------------------------------------------------
    # STEP 1 — Train final LightGBM
    # -------------------------------------------------------------------------
    print(f"\n[Step 1] Training final LightGBM on {len(FINAL_FEATURES)} features...")
    if not DROP_INCOME_TYPE:
        # Use Model A already fitted or refit cleanly
        final_model = clf_a
    else:
        final_model = clf_b

    best_iter = final_model.best_iteration_
    val_auc = float(final_model.best_score_["valid_0"]["auc"])
    print(f"  Best iteration     : {best_iter}")
    print(f"  Validation AUC     : {val_auc:.5f}")

    # -------------------------------------------------------------------------
    # STEP 2 — Calibrate
    # -------------------------------------------------------------------------
    print("\n[Step 2] Fitting Isotonic Regression calibrator on validation set...")
    val_raw_probs = final_model.predict_proba(val_df[FINAL_FEATURES])[:, 1]

    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(val_raw_probs, y_val)

    val_calib_probs = np.clip(calibrator.predict(val_raw_probs), 0.005, 1.0)
    calibrator_path = ml_dir / "calibrator.pkl"
    with open(calibrator_path, "wb") as f:
        pickle.dump(calibrator, f)
    print(f"  Saved calibrator to: {calibrator_path}")

    # -------------------------------------------------------------------------
    # STEP 3 — Decile table on test set with equal bin sizes
    # -------------------------------------------------------------------------
    print("\n[Step 3] Evaluating Decile Calibration on Test Set (Equal Bin Sizes)...")
    test_raw_probs = final_model.predict_proba(test_df[FINAL_FEATURES])[:, 1]
    test_calib_probs = np.clip(calibrator.predict(test_raw_probs), 0.005, 1.0)

    test_df["raw_prob"] = test_raw_probs
    test_df["calib_prob"] = test_calib_probs

    # Equal bin sizes using rank(method='first')
    scores_series = pd.Series(test_calib_probs)
    test_df["decile"] = pd.qcut(scores_series.rank(method="first"), q=10, labels=False) + 1

    decile_table = test_df.groupby("decile").agg(
        count=("TARGET", "count"),
        mean_calib_prob=("calib_prob", "mean"),
        actual_default_rate=("TARGET", "mean")
    ).reset_index()

    print("Test Set Decile Calibration Table:")
    print(decile_table.to_string(
        index=False,
        formatters={
            "decile": lambda x: f"{x:6d}",
            "count": lambda x: f"{x:7,d}",
            "mean_calib_prob": lambda x: f"{x:16.4f}",
            "actual_default_rate": lambda x: f"{x:20.4f}",
        }
    ))

    # -------------------------------------------------------------------------
    # STEP 4 — Thresholds
    # -------------------------------------------------------------------------
    print("\n[Step 4] Recomputing decision thresholds on validation set...")
    approve_below = float(np.percentile(val_calib_probs, 60))
    deny_above = float(np.percentile(val_calib_probs, 85))

    thresholds_dict = {
        "approve_below": approve_below,
        "deny_above": deny_above
    }
    thresholds_path = ml_dir / "thresholds.json"
    with open(thresholds_path, "w") as f:
        json.dump(thresholds_dict, f, indent=2)

    print(f"  Approve below (bottom 60%): {approve_below:.5f}")
    print(f"  Deny above    (top 15%)   : {deny_above:.5f}")
    print(f"  Refer for review          : [{approve_below:.5f}, {deny_above:.5f}]")
    print(f"  Saved thresholds configuration to: {thresholds_path}")

    # Evaluate on test set
    conds = [
        test_df["calib_prob"] < approve_below,
        (test_df["calib_prob"] >= approve_below) & (test_df["calib_prob"] <= deny_above),
        test_df["calib_prob"] > deny_above,
    ]
    bands = ["Approve", "Refer", "Deny"]
    test_df["decision_band"] = np.select(conds, bands, default="Refer")

    total_test = len(test_df)
    band_summary = []
    for b in bands:
        sub = test_df[test_df["decision_band"] == b]
        b_cnt = len(sub)
        b_rate = sub["TARGET"].mean() if b_cnt > 0 else 0.0
        b_pct = (b_cnt / total_test) * 100
        band_summary.append({
            "Band": b,
            "Count": b_cnt,
            "Actual Default Rate": b_rate,
            "% of Applicants": b_pct,
        })
    df_bands = pd.DataFrame(band_summary)
    print("\nTest Set Threshold Decision Bands:")
    print(df_bands.to_string(
        index=False,
        formatters={
            "Count": lambda x: f"{x:8,d}",
            "Actual Default Rate": lambda x: f"{x:20.4f}",
            "% of Applicants": lambda x: f"{x:14.2f}%",
        }
    ))

    approve_rate = df_bands.loc[df_bands["Band"] == "Approve", "Actual Default Rate"].values[0]
    deny_rate = df_bands.loc[df_bands["Band"] == "Deny", "Actual Default Rate"].values[0]
    deny_approve_ratio = deny_rate / approve_rate if approve_rate > 0 else np.nan
    print(f"\nDeny to Approve Default Rate Ratio: {deny_approve_ratio:.2f}x")

    # -------------------------------------------------------------------------
    # STEP 5 — SHAP on test set
    # -------------------------------------------------------------------------
    print("\n[Step 5] Computing SHAP values on test set...")
    explainer = shap.TreeExplainer(final_model)
    shap_raw = explainer.shap_values(test_df[FINAL_FEATURES])
    if isinstance(shap_raw, list):
        shap_vals = shap_raw[1]
    else:
        shap_vals = shap_raw

    shap_df = pd.DataFrame(shap_vals, columns=FINAL_FEATURES)

    print("\nSHAP Direction Check (Bottom 20% vs Top 20% Quintiles):")
    direction_features = [
        "employment_years",
        "late_payment_share",
        "prev_refusal_rate",
        "installments_count",
        "underpayment_share"
    ]
    dir_rows = []
    for feat in direction_features:
        s = test_df[feat]
        valid = s.notna()
        q20 = s[valid].quantile(0.20)
        q80 = s[valid].quantile(0.80)

        bottom_mean = shap_df.loc[valid & (s <= q20), feat].mean()
        top_mean = shap_df.loc[valid & (s >= q80), feat].mean()
        diff = top_mean - bottom_mean

        dir_rows.append({
            "Feature": feat,
            "Bottom 20% Cutoff": f"<= {q20:.2f}",
            "Bottom Mean SHAP": bottom_mean,
            "Top 20% Cutoff": f">= {q80:.2f}",
            "Top Mean SHAP": top_mean,
            "Delta (Top - Bottom)": diff
        })
    df_dir = pd.DataFrame(dir_rows)
    print(df_dir.to_string(
        index=False,
        formatters={
            "Bottom Mean SHAP": lambda x: f"{x:+8.4f}",
            "Top Mean SHAP": lambda x: f"{x:+8.4f}",
            "Delta (Top - Bottom)": lambda x: f"{x:+8.4f}"
        }
    ))

    # -------------------------------------------------------------------------
    # STEP 6 — Reason code selection with dedup rule
    # -------------------------------------------------------------------------
    print("\n[Step 6] Computing reason codes with loan-size dedup rule...")
    # Extract eligible SHAP values
    elig_indices = [FINAL_FEATURES.index(f) for f in ELIGIBLE_REASON_FEATURES]
    elig_shap = shap_vals[:, elig_indices]

    n_samples = len(test_df)
    reason_1 = []
    reason_2 = []
    reason_3 = []
    shap_1 = []
    shap_2 = []
    shap_3 = []

    # Dedup rule between AMT_CREDIT and credit_income_ratio
    amt_credit_idx = ELIGIBLE_REASON_FEATURES.index("AMT_CREDIT")
    cir_idx = ELIGIBLE_REASON_FEATURES.index("credit_income_ratio")

    for i in range(n_samples):
        row_shap = elig_shap[i]
        # Rank features descending by signed SHAP value
        ranked_order = np.argsort(-row_shap)

        # Select top features with dedup
        selected = []
        for idx in ranked_order:
            feat_name = ELIGIBLE_REASON_FEATURES[idx]

            # Check dedup conflict with loan_size group
            if feat_name in ("AMT_CREDIT", "credit_income_ratio"):
                other_feat = "credit_income_ratio" if feat_name == "AMT_CREDIT" else "AMT_CREDIT"
                if other_feat in selected:
                    # Conflict: compare absolute SHAP values
                    curr_abs = abs(row_shap[idx])
                    other_idx = ELIGIBLE_REASON_FEATURES.index(other_feat)
                    other_abs = abs(row_shap[other_idx])
                    if curr_abs > other_abs:
                        # Replace the other feature
                        pos = selected.index(other_feat)
                        selected[pos] = feat_name
                    # In either case, do not add as a second entry
                    continue

            selected.append(feat_name)
            if len(selected) == 3:
                break

        # Fallback if fewer than 3
        if len(selected) < 3:
            for idx in ranked_order:
                fn = ELIGIBLE_REASON_FEATURES[idx]
                if fn not in selected:
                    selected.append(fn)
                if len(selected) == 3:
                    break

        r1, r2, r3 = selected[0], selected[1], selected[2]
        s1 = row_shap[ELIGIBLE_REASON_FEATURES.index(r1)]
        s2 = row_shap[ELIGIBLE_REASON_FEATURES.index(r2)]
        s3 = row_shap[ELIGIBLE_REASON_FEATURES.index(r3)]

        reason_1.append(r1)
        reason_2.append(r2)
        reason_3.append(r3)
        shap_1.append(s1)
        shap_2.append(s2)
        shap_3.append(s3)

    df_shap_test = pd.DataFrame({
        "SK_ID_CURR": test_df["SK_ID_CURR"].values,
        "reason_code_1": reason_1,
        "reason_code_2": reason_2,
        "reason_code_3": reason_3,
        "shap_1": shap_1,
        "shap_2": shap_2,
        "shap_3": shap_3,
    })
    shap_test_path = ml_dir / "shap_test.parquet"
    df_shap_test.to_parquet(shap_test_path, index=False)
    print(f"  Saved test reason codes (with dedup) to: {shap_test_path} ({len(df_shap_test):,} rows)")

    # -------------------------------------------------------------------------
    # STEP 7 — Demo pool
    # -------------------------------------------------------------------------
    print("\n[Step 7] Recreating Demo Pool (200 rows: 50 thin, 150 thick, seed=42)...")
    test_thin = test_df[test_df["thin_file"] == 1]
    test_thick = test_df[test_df["thin_file"] == 0]

    demo_thin = test_thin.sample(n=50, random_state=42)
    demo_thick = test_thick.sample(n=150, random_state=42)
    demo_pool = (
        pd.concat([demo_thin, demo_thick])
        .sample(frac=1.0, random_state=42)
        .reset_index(drop=True)
    )
    demo_pool.to_parquet(demo_pool_path, index=False)

    train_ids = set(train_df["SK_ID_CURR"])
    val_ids = set(val_df["SK_ID_CURR"])
    demo_ids = set(demo_pool["SK_ID_CURR"])

    train_overlap = len(demo_ids & train_ids)
    val_overlap = len(demo_ids & val_ids)

    assert train_overlap == 0, f"Demo pool leaks into train: {train_overlap} IDs"
    assert val_overlap == 0, f"Demo pool leaks into validation: {val_overlap} IDs"
    demo_status = "PASS"
    print(f"  Saved demo pool to: {demo_pool_path}")
    print(f"  Demo pool leakage check: {demo_status} (0 train overlap, 0 val overlap)")

    # -------------------------------------------------------------------------
    # STEP 8 — Save all artifacts
    # -------------------------------------------------------------------------
    print("\n[Step 8] Saving all pipeline artifacts...")

    # ml/model.pkl
    model_path = ml_dir / "model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(final_model, f)
    print(f"  - Saved model to: {model_path}")

    # ml/calibrator.pkl
    print(f"  - Saved calibrator to: {calibrator_path}")

    # ml/feature_list.json
    feature_list_path = ml_dir / "feature_list.json"
    with open(feature_list_path, "w") as f:
        json.dump(FINAL_FEATURES, f, indent=2)
    print(f"  - Saved feature list ({len(FINAL_FEATURES)} features) to: {feature_list_path}")

    # ml/feature_importance.csv
    feature_imp_path = ml_dir / "feature_importance.csv"
    mean_abs_shap = np.mean(np.abs(shap_vals), axis=0)
    df_fi = pd.DataFrame({
        "feature": FINAL_FEATURES,
        "mean_abs_shap": mean_abs_shap
    }).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)
    df_fi.to_csv(feature_imp_path, index=False)
    print(f"  - Saved feature importance to: {feature_imp_path}")

    # ml/shap_test.parquet already saved in Step 6
    print(f"  - Saved reason codes to: {shap_test_path}")

    # ml/thresholds.json already saved in Step 4
    print(f"  - Saved thresholds to: {thresholds_path}")

    # ml/encoders/
    if not DROP_INCOME_TYPE:
        enc_income_path = encoders_dir / "NAME_INCOME_TYPE.pkl"
        with open(enc_income_path, "wb") as f:
            pickle.dump(le_income, f)
        print(f"  - Saved encoder to: {enc_income_path}")

    # Clean up housing encoder if present
    housing_enc_file = encoders_dir / "NAME_HOUSING_TYPE.pkl"
    if housing_enc_file.exists():
        housing_enc_file.unlink()

    # -------------------------------------------------------------------------
    # STEP 9 — Update ml/feature_registry.yaml
    # -------------------------------------------------------------------------
    print("\n[Step 9] Updating ml/feature_registry.yaml...")
    registry_path = ml_dir / "feature_registry.yaml"

    eligible_entries = [
        {
            "feature": "employment_years",
            "description": "Years of verified employment history",
            "reason_phrase": "Short employment tenure indicates limited financial stability",
            "nan_reason_phrase": "No verifiable employment history on record",
            "direction": "low increases risk",
            "alt_data": False,
        },
        {
            "feature": "late_payment_share",
            "description": "Proportion of prior loan installment payments made past due date",
            "reason_phrase": "High proportion of late payments on prior loans",
            "direction": "high increases risk",
            "alt_data": True,
        },
        {
            "feature": "prev_refusal_rate",
            "description": "Proportion of past credit applications that were declined",
            "reason_phrase": "High rate of prior credit application refusals",
            "direction": "high increases risk",
            "alt_data": False,
        },
        {
            "feature": "installments_count",
            "description": "Total count of past loan installment payments completed",
            "reason_phrase": "Limited installment payment history on record",
            "direction": "low increases risk",
            "alt_data": True,
        },
        {
            "feature": "underpayment_share",
            "description": "Proportion of past installments where payment was less than amount due",
            "reason_phrase": "High proportion of underpayments on prior loans",
            "direction": "high increases risk",
            "alt_data": True,
        },
        {
            "feature": "mean_days_late",
            "description": "Average number of days payments were made past due date",
            "reason_phrase": "Average days late on prior loan payments is elevated",
            "direction": "high increases risk",
            "alt_data": True,
        },
        {
            "feature": "AMT_CREDIT",
            "description": "Total credit amount requested on current application",
            "reason_phrase": "Requested loan amount is high",
            "dedup_group": "loan_size",
            "direction": "high increases risk",
            "alt_data": False,
        },
        {
            "feature": "credit_income_ratio",
            "description": "Ratio of requested loan credit amount to applicant total annual income",
            "reason_phrase": "Ratio of requested credit to annual income is high",
            "dedup_group": "loan_size",
            "direction": "high increases risk",
            "alt_data": False,
        },
        {
            "feature": "annuity_income_ratio",
            "description": "Ratio of monthly loan annuity obligation to applicant annual income",
            "reason_phrase": "Ratio of loan repayment amount to income is high",
            "direction": "high increases risk",
            "alt_data": False,
        },
        {
            "feature": "thin_file",
            "description": "Binary indicator of zero formal credit bureau tradelines",
            "reason_phrase": "Limited or no credit bureau history on record",
            "direction": "high increases risk",
            "alt_data": False,
        },
    ]

    excluded_entries = []
    if not DROP_INCOME_TYPE:
        excluded_entries.append({
            "feature": "NAME_INCOME_TYPE",
            "reason": "Structural attribute excluded from reason codes per fair lending disclosure policy. Audited for disparate impact on fairness dashboard."
        })
    else:
        excluded_entries.append({
            "feature": "NAME_INCOME_TYPE",
            "reason": "Dropped from model, AUC cost under 0.003."
        })

    excluded_entries.append({
        "feature": "NAME_HOUSING_TYPE",
        "reason": "Dropped from model, AUC cost under 0.003. Structural attribute excluded from reason codes."
    })

    registry_dict = {
        "eligible_features": eligible_entries,
        "excluded_features": excluded_entries,
    }

    with open(registry_path, "w") as f:
        yaml.dump(registry_dict, f, sort_keys=False, default_flow_style=False)
    print(f"Confirmation: Successfully updated feature registry at {registry_path}")

    # -------------------------------------------------------------------------
    # STEP 10 — Print final summary
    # -------------------------------------------------------------------------
    print("\n" + "=" * 80)
    print("STEP 10: FINAL SUMMARY")
    print("=" * 80)
    calib_test_auc = roc_auc_score(y_test, test_calib_probs)
    thin_calib_auc = roc_auc_score(test_df.loc[test_df["thin_file"] == 1, "TARGET"], test_df.loc[test_df["thin_file"] == 1, "calib_prob"])
    thick_calib_auc = roc_auc_score(test_df.loc[test_df["thin_file"] == 0, "TARGET"], test_df.loc[test_df["thin_file"] == 0, "calib_prob"])

    print(f"Final feature count               : {len(FINAL_FEATURES)}")
    print(f"Final feature list                : {FINAL_FEATURES}")
    print(f"Best iteration                    : {best_iter}")
    print(f"Validation AUC                    : {val_auc:.5f}")
    print(f"Calibrated test AUC               : {calib_test_auc:.5f}")
    print(f"Thin file calibrated AUC          : {thin_calib_auc:.5f}")
    print(f"Thick file calibrated AUC         : {thick_calib_auc:.5f}")
    print("\nDecision Bands on Test Set:")
    for _, row in df_bands.iterrows():
        print(f"  {row['Band']:7s}: Count = {row['Count']:6,d} ({row['% of Applicants']:5.2f}%) | Actual Default Rate = {row['Actual Default Rate']:.4f}")
    print(f"Deny to approve default rate ratio: {deny_approve_ratio:.2f}x")

    print("\nTop 5 SHAP features:")
    for rank, row in df_fi.head(5).iterrows():
        print(f"  {rank+1}. {row['feature']:25s} : {row['mean_abs_shap']:.5f}")

    print("\nSHAP direction check results:")
    for _, row in df_dir.iterrows():
        print(f"  {row['Feature']:20s}: Bottom={row['Bottom Mean SHAP']:+.4f} | Top={row['Top Mean SHAP']:+.4f} | Delta={row['Delta (Top - Bottom)']:+.4f}")

    print(f"\nDemo pool check result            : {demo_status}")

    print("\nFeatures excluded from reason codes and rationale:")
    for ex in excluded_entries:
        print(f"  - {ex['feature']}: {ex['reason']}")

    elapsed = time.time() - total_start
    print(f"\nComplete pipeline finished successfully in {elapsed:.1f} seconds.")
    print("=" * 80)


if __name__ == "__main__":
    main()
