# backend/inference.py

import json
import pickle
from pathlib import Path
import numpy as np
import pandas as pd
import shap

# ─── LOAD PRODUCTION ML ARTIFACTS (once at module level) ──────────────────────
ML_DIR = Path(__file__).resolve().parent.parent / "ml"

with open(ML_DIR / "model.pkl", "rb") as f:
    MODEL = pickle.load(f)

with open(ML_DIR / "calibrator.pkl", "rb") as f:
    CALIBRATOR = pickle.load(f)

with open(ML_DIR / "thresholds.json", "r") as f:
    THRESHOLDS = json.load(f)

with open(ML_DIR / "feature_list.json", "r") as f:
    FEATURE_LIST = json.load(f)

# Load TreeExplainer once at module level
EXPLAINER = shap.TreeExplainer(MODEL)

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
    "bureau_active_credits_count",
]


def run_inference(applicant_data: dict) -> dict:
    """
    Run complete ML risk scoring and SHAP reason code extraction.

    Parameters:
    - applicant_data: dict containing feature values and optional applicant_id

    Returns:
    - dict with applicant_id, raw_probability, calibrated_probability,
      decision_band, is_thin_file, and top 4 deduplicated shap_features
    """
    # Step 2: Build feature vector DataFrame in exact order of FEATURE_LIST
    row_dict = {}
    for feat in FEATURE_LIST:
        val = applicant_data.get(feat, 0.0)
        if val is None:
            val = 0.0
        row_dict[feat] = float(val)

    df_row = pd.DataFrame([row_dict], columns=FEATURE_LIST)

    # Step 3: ML inference & calibration
    raw_prob = float(MODEL.predict_proba(df_row)[:, 1][0])
    calib_prob = float(np.clip(CALIBRATOR.predict([raw_prob]), 0.005, 1.0)[0])

    # Step 4: Decision band
    if calib_prob < THRESHOLDS["approve_below"]:
        decision_band = "Approve"
    elif calib_prob > THRESHOLDS["deny_above"]:
        decision_band = "Deny"
    else:
        decision_band = "Refer"

    # Step 5: SHAP values & Top 4 reason codes
    shap_raw = EXPLAINER.shap_values(df_row)
    if isinstance(shap_raw, list):
        shap_vals = shap_raw[1][0] if len(shap_raw) > 1 else shap_raw[0][0]
    elif len(shap_raw.shape) == 3:
        shap_vals = shap_raw[0, :, 1]
    else:
        shap_vals = shap_raw[0]

    feat_to_shap = {feat: float(shap_vals[i]) for i, feat in enumerate(FEATURE_LIST)}

    # Filter to eligible features
    eligible = [
        (feat, feat_to_shap.get(feat, 0.0))
        for feat in ELIGIBLE_REASON_FEATURES
        if feat in FEATURE_LIST or feat in df_row.columns
    ]

    # Sort eligible features by signed SHAP descending
    eligible.sort(key=lambda x: x[1], reverse=True)

    # Dedup rule: AMT_CREDIT vs credit_income_ratio cannot BOTH appear
    amt_shap = feat_to_shap.get("AMT_CREDIT", 0.0)
    cir_shap = feat_to_shap.get("credit_income_ratio", 0.0)

    discard_feature = None
    if "AMT_CREDIT" in [x[0] for x in eligible] and "credit_income_ratio" in [x[0] for x in eligible]:
        if abs(amt_shap) >= abs(cir_shap):
            discard_feature = "credit_income_ratio"
        else:
            discard_feature = "AMT_CREDIT"

    selected = []
    for feat, s_val in eligible:
        if feat == discard_feature:
            continue
        selected.append((feat, s_val))
        if len(selected) == 4:
            break

    shap_features = [
        {
            "feature_name": feat,
            "value": float(df_row[feat].iloc[0]) if feat in df_row.columns else float(applicant_data.get(feat, 0.0)),
            "shap": float(s_val),
        }
        for feat, s_val in selected
    ]

    # Step 6: Return dict
    return {
        "applicant_id": str(applicant_data.get("applicant_id", "UNKNOWN")),
        "raw_probability": round(raw_prob, 6),
        "calibrated_probability": round(calib_prob, 6),
        "decision_band": decision_band,
        "is_thin_file": bool(applicant_data.get("thin_file", 0)),
        "shap_features": shap_features,
    }
