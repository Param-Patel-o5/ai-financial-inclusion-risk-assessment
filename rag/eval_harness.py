import json
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables (.env)
load_dotenv()

from rag.retriever import retrieve
from rag.generator import generate, AdverseActionNotice

# ─── 12 HARDCODED MOCK APPLICANT PROFILES ─────────────────────────────────────
# Dimensions covered:
# - decision_band: "Approve" (2), "Refer" (4), "Deny" (6)
# - thin_file flag: True (6 profiles), False (6 profiles)
# - shap feature variety: 16 distinct features used across profiles
# - calibrated_prob: spread across <0.07474, 0.07-0.13, and >0.13375
TEST_POOL = [
    {
        "applicant_id": "EVAL_001",
        "decision_band": "Deny",
        "calibrated_prob": 0.187,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "late_payment_share",       "value": 0.42, "shap": 0.31},
            {"feature_name": "prev_refusal_rate",        "value": 0.80, "shap": 0.22},
            {"feature_name": "mean_days_late",           "value": 18.5, "shap": 0.19},
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.14},
        ],
    },
    {
        "applicant_id": "EVAL_002",
        "decision_band": "Deny",
        "calibrated_prob": 0.245,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "underpayment_share",       "value": 0.35, "shap": 0.28},
            {"feature_name": "credit_income_ratio",      "value": 4.50, "shap": 0.24},
            {"feature_name": "prev_refusal_rate",        "value": 0.65, "shap": 0.18},
            {"feature_name": "employment_years",         "value": 0.8,  "shap": 0.13},
        ],
    },
    {
        "applicant_id": "EVAL_003",
        "decision_band": "Deny",
        "calibrated_prob": 0.162,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.29},
            {"feature_name": "annuity_income_ratio",     "value": 0.38, "shap": 0.21},
            {"feature_name": "mean_days_late",           "value": 45.0, "shap": 0.17},
            {"feature_name": "bureau_active_credits_count", "value": 1.0, "shap": 0.12},
        ],
    },
    {
        "applicant_id": "EVAL_004",
        "decision_band": "Deny",
        "calibrated_prob": 0.210,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "installments_count",       "value": 4.0,  "shap": 0.25},
            {"feature_name": "credit_income_ratio",      "value": 3.80, "shap": 0.20},
            {"feature_name": "employment_years",         "value": 0.5,  "shap": 0.16},
            {"feature_name": "underpayment_share",       "value": 0.28, "shap": 0.11},
        ],
    },
    {
        "applicant_id": "EVAL_005",
        "decision_band": "Deny",
        "calibrated_prob": 0.155,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.29},
            {"feature_name": "AMT_CREDIT",               "value": 650000.0, "shap": 0.18},
            {"feature_name": "late_payment_share",       "value": 0.28, "shap": 0.15},
            {"feature_name": "bureau_active_credits_count", "value": 0.0, "shap": 0.11},
        ],
    },
    {
        "applicant_id": "EVAL_006",
        "decision_band": "Deny",
        "calibrated_prob": 0.178,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "prev_refusal_rate",        "value": 0.65, "shap": 0.23},
            {"feature_name": "mean_days_late",           "value": 14.0, "shap": 0.19},
            {"feature_name": "underpayment_share",       "value": 0.22, "shap": 0.14},
            {"feature_name": "installments_count",       "value": 5.0,  "shap": 0.10},
        ],
    },
    {
        "applicant_id": "EVAL_007",
        "decision_band": "Refer",
        "calibrated_prob": 0.095,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.14},
            {"feature_name": "installments_count",       "value": 6.0,  "shap": 0.11},
            {"feature_name": "credit_income_ratio",      "value": 3.20, "shap": 0.09},
            {"feature_name": "bureau_active_credits_count", "value": 2.0, "shap": 0.07},
        ],
    },
    {
        "applicant_id": "EVAL_008",
        "decision_band": "Refer",
        "calibrated_prob": 0.112,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "annuity_income_ratio",     "value": 0.29, "shap": 0.13},
            {"feature_name": "mean_days_late",           "value": 8.0,  "shap": 0.10},
            {"feature_name": "employment_years",         "value": 1.2,  "shap": 0.08},
            {"feature_name": "underpayment_share",       "value": 0.12, "shap": 0.06},
        ],
    },
    {
        "applicant_id": "EVAL_009",
        "decision_band": "Refer",
        "calibrated_prob": 0.082,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.15},
            {"feature_name": "bureau_active_credits_count", "value": 1.0, "shap": 0.09},
            {"feature_name": "annuity_income_ratio",     "value": 0.24, "shap": 0.07},
            {"feature_name": "installments_count",       "value": 7.0,  "shap": 0.05},
        ],
    },
    {
        "applicant_id": "EVAL_010",
        "decision_band": "Refer",
        "calibrated_prob": 0.125,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "late_payment_share",       "value": 0.18, "shap": 0.12},
            {"feature_name": "underpayment_share",       "value": 0.15, "shap": 0.10},
            {"feature_name": "credit_income_ratio",      "value": 2.80, "shap": 0.08},
            {"feature_name": "AMT_CREDIT",               "value": 420000.0, "shap": 0.06},
        ],
    },
    {
        "applicant_id": "EVAL_011",
        "decision_band": "Approve",
        "calibrated_prob": 0.035,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.04},
            {"feature_name": "credit_income_ratio",      "value": 1.50, "shap": 0.03},
            {"feature_name": "installments_count",       "value": 12.0, "shap": 0.02},
            {"feature_name": "bureau_active_credits_count", "value": 3.0, "shap": 0.01},
        ],
    },
    {
        "applicant_id": "EVAL_012",
        "decision_band": "Approve",
        "calibrated_prob": 0.048,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "employment_years",         "value": 6.5,  "shap": 0.05},
            {"feature_name": "annuity_income_ratio",     "value": 0.14, "shap": 0.03},
            {"feature_name": "AMT_CREDIT",               "value": 180000.0, "shap": 0.02},
            {"feature_name": "late_payment_share",       "value": 0.05, "shap": 0.01},
        ],
    },
    {
        "applicant_id": "EVAL_013",
        "decision_band": "Deny",
        "calibrated_prob": 0.224,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.32},
            {"feature_name": "credit_income_ratio",      "value": 6.20, "shap": 0.26},
            {"feature_name": "employment_years",         "value": 0.4,  "shap": 0.17},
            {"feature_name": "annuity_income_ratio",     "value": 0.35, "shap": 0.12},
        ],
    },
    {
        "applicant_id": "EVAL_014",
        "decision_band": "Deny",
        "calibrated_prob": 0.198,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "late_payment_share",       "value": 0.38, "shap": 0.29},
            {"feature_name": "mean_days_late",           "value": 22.0, "shap": 0.23},
            {"feature_name": "prev_refusal_rate",        "value": 0.70, "shap": 0.19},
            {"feature_name": "underpayment_share",       "value": 0.25, "shap": 0.14},
        ],
    },
    {
        "applicant_id": "EVAL_015",
        "decision_band": "Deny",
        "calibrated_prob": 0.172,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.27},
            {"feature_name": "installments_count",       "value": 3.0,  "shap": 0.21},
            {"feature_name": "AMT_CREDIT",               "value": 580000.0, "shap": 0.16},
            {"feature_name": "bureau_active_credits_count", "value": 0.0, "shap": 0.11},
        ],
    },
    {
        "applicant_id": "EVAL_016",
        "decision_band": "Refer",
        "calibrated_prob": 0.108,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.15},
            {"feature_name": "annuity_income_ratio",     "value": 0.27, "shap": 0.11},
            {"feature_name": "installments_count",       "value": 8.0,  "shap": 0.08},
            {"feature_name": "credit_income_ratio",      "value": 2.90, "shap": 0.06},
        ],
    },
    {
        "applicant_id": "EVAL_017",
        "decision_band": "Refer",
        "calibrated_prob": 0.119,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "credit_income_ratio",      "value": 3.40, "shap": 0.13},
            {"feature_name": "late_payment_share",       "value": 0.12, "shap": 0.10},
            {"feature_name": "employment_years",         "value": 2.2,  "shap": 0.07},
            {"feature_name": "bureau_active_credits_count", "value": 5.0, "shap": 0.05},
        ],
    },
    {
        "applicant_id": "EVAL_018",
        "decision_band": "Refer",
        "calibrated_prob": 0.088,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.14},
            {"feature_name": "employment_years",         "value": 1.1,  "shap": 0.09},
            {"feature_name": "installments_count",       "value": 9.0,  "shap": 0.07},
            {"feature_name": "bureau_active_credits_count", "value": 1.0, "shap": 0.04},
        ],
    },
    {
        "applicant_id": "EVAL_019",
        "decision_band": "Approve",
        "calibrated_prob": 0.028,
        "is_thin_file": False,
        "shap_features": [
            {"feature_name": "employment_years",         "value": 8.5,  "shap": 0.05},
            {"feature_name": "credit_income_ratio",      "value": 1.20, "shap": 0.03},
            {"feature_name": "late_payment_share",       "value": 0.0,  "shap": 0.02},
            {"feature_name": "bureau_active_credits_count", "value": 6.0, "shap": 0.01},
        ],
    },
    {
        "applicant_id": "EVAL_020",
        "decision_band": "Approve",
        "calibrated_prob": 0.042,
        "is_thin_file": True,
        "shap_features": [
            {"feature_name": "thin_file",                "value": 1.0,  "shap": 0.04},
            {"feature_name": "installments_count",       "value": 16.0, "shap": 0.03},
            {"feature_name": "annuity_income_ratio",     "value": 0.12, "shap": 0.02},
            {"feature_name": "credit_income_ratio",      "value": 1.40, "shap": 0.01},
        ],
    },
]


def run_evaluation():
    print(f"Starting RAG Evaluation Harness ({len(TEST_POOL)} profiles)...")
    print("-" * 60)

    run_records = []
    retrieval_latencies = []
    generation_latencies = []
    schema_valid_count = 0
    feat_hallucination_count = 0
    cite_hallucination_count = 0
    prohibited_term_count = 0
    completed_count = 0
    failed_count = 0

    total_profiles = len(TEST_POOL)

    for i, profile in enumerate(TEST_POOL, 1):
        app_id = profile["applicant_id"]
        band = profile["decision_band"]
        is_thin = profile["is_thin_file"]
        prob = profile["calibrated_prob"]
        shap_feats = profile["shap_features"]

        try:
            # Step 1: Retrieval
            t0 = time.perf_counter()
            retrieval_result = retrieve(
                shap_features=shap_feats,
                decision_band=band,
                is_thin_file=is_thin,
                applicant_id=app_id,
            )
            retrieval_lat = round(time.perf_counter() - t0, 3)
            retrieval_latencies.append(retrieval_lat)

            retrieved_clauses = retrieval_result.get("retrieved_clauses", [])
            retrieved_clause_ids = [c["chunk_id"] for c in retrieved_clauses]

            # Step 2: Generation
            t1 = time.perf_counter()
            generation_result = generate(
                applicant_id=app_id,
                decision_band=band,
                calibrated_prob=prob,
                is_thin_file=is_thin,
                shap_features=shap_feats,
                retrieved_clauses=retrieved_clauses,
            )
            gen_lat = round(time.perf_counter() - t1, 3)
            generation_latencies.append(gen_lat)

            # Step 3: Schema validation
            notice_dict = generation_result.get("notice", {})
            schema_valid = False
            try:
                AdverseActionNotice(**notice_dict)
                schema_valid = True
                schema_valid_count += 1
            except Exception:
                schema_valid = False

            # Step 4: Audit flags inspection
            audit_flags = generation_result.get("audit_flags", [])

            has_feat_hallucination = any("HALLUCINATED_FEATURE" in f for f in audit_flags)
            if has_feat_hallucination:
                feat_hallucination_count += 1

            has_cite_hallucination = any("HALLUCINATED_CITATION" in f for f in audit_flags)
            if has_cite_hallucination:
                cite_hallucination_count += 1

            has_prohibited = any("PROHIBITED" in f for f in audit_flags)
            if has_prohibited:
                prohibited_term_count += 1

            completed_count += 1

            run_records.append({
                "applicant_id": app_id,
                "decision_band": band,
                "is_thin_file": is_thin,
                "schema_valid": schema_valid,
                "audit_flags": audit_flags,
                "retrieval_latency_s": retrieval_lat,
                "generation_latency_s": gen_lat,
                "notice": notice_dict,
                "retrieved_clause_ids": retrieved_clause_ids,
                "status": "ok",
            })

            total_lat = retrieval_lat + gen_lat
            print(f"[{i}/{total_profiles}] {app_id} | {band} | thin={is_thin} | flags={len(audit_flags)} | latency={total_lat:.2f}s")

        except Exception as e:
            failed_count += 1
            run_records.append({
                "applicant_id": app_id,
                "decision_band": band,
                "is_thin_file": is_thin,
                "schema_valid": False,
                "audit_flags": [f"EXECUTION_ERROR: {str(e)}"],
                "retrieval_latency_s": 0.0,
                "generation_latency_s": 0.0,
                "notice": {},
                "retrieved_clause_ids": [],
                "status": "failed",
            })
            print(f"[{i}/{total_profiles}] {app_id} | {band} | thin={is_thin} | FAILED ({str(e)})")

        # Rate limit protection: 2-second pause between calls
        if i < total_profiles:
            time.sleep(2.0)

    # ─── AGGREGATE METRICS ────────────────────────────────────────────────────
    schema_validity_rate = round((schema_valid_count / total_profiles) * 100, 1)
    feat_hallucination_rate = round((feat_hallucination_count / total_profiles) * 100, 1)
    cite_hallucination_rate = round((cite_hallucination_count / total_profiles) * 100, 1)
    prohibited_term_rate = round((prohibited_term_count / total_profiles) * 100, 1)

    mean_retrieval_lat = round(sum(retrieval_latencies) / len(retrieval_latencies), 2) if retrieval_latencies else 0.0
    mean_gen_lat = round(sum(generation_latencies) / len(generation_latencies), 2) if generation_latencies else 0.0

    # Verification checks against targets
    pass_schema = (schema_validity_rate == 100.0)
    pass_feat = (feat_hallucination_rate == 0.0)
    pass_cite = (cite_hallucination_rate == 0.0)
    pass_prohibited = (prohibited_term_rate == 0.0)
    all_passed = pass_schema and pass_feat and pass_cite and pass_prohibited and (failed_count == 0)

    # ─── CONSOLE OUTPUT TABLE ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"RAG PIPELINE EVALUATION RESULTS — {total_profiles} PROFILES")
    print("=" * 60)
    print(f"{'Metric':<32} {'Value':<10} {'Target':<8} {'Pass?'}")
    print("-" * 60)
    print(f"{'Schema Validity Rate':<32} {f'{schema_validity_rate}%':<10} {'100%':<8} {'✓' if pass_schema else '✗'}")
    print(f"{'Feature Hallucination Rate':<32} {f'{feat_hallucination_rate}%':<10} {'0%':<8} {'✓' if pass_feat else '✗'}")
    print(f"{'Citation Hallucination Rate':<32} {f'{cite_hallucination_rate}%':<10} {'0%':<8} {'✓' if pass_cite else '✗'}")
    print(f"{'Prohibited Term Violation Rate':<32} {f'{prohibited_term_rate}%':<10} {'0%':<8} {'✓' if pass_prohibited else '✗'}")
    print(f"{'Mean Retrieval Latency':<32} {f'{mean_retrieval_lat}s':<10} {'—':<8} {'—'}")
    print(f"{'Mean Generation Latency':<32} {f'{mean_gen_lat}s':<10} {'—':<8} {'—'}")
    print("-" * 60)
    print(f"Runs Completed: {completed_count}/{total_profiles}   Failed: {failed_count}")
    print("=" * 60)

    # ─── JSON OUTPUT FILE ─────────────────────────────────────────────────────
    eval_results = {
        "summary": {
            "total_profiles": total_profiles,
            "completed": completed_count,
            "failed": failed_count,
            "schema_validity_rate": schema_validity_rate,
            "feature_hallucination_rate": feat_hallucination_rate,
            "citation_hallucination_rate": cite_hallucination_rate,
            "prohibited_term_violation_rate": prohibited_term_rate,
            "mean_retrieval_latency_s": mean_retrieval_lat,
            "mean_generation_latency_s": mean_gen_lat,
        },
        "runs": run_records,
    }

    out_path = Path(__file__).resolve().parent / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(eval_results, f, indent=2)

    print(f"\n[OK] Full evaluation results saved to: {out_path}")

    # Exit code: 0 on success, 1 on any target failure
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    run_evaluation()
