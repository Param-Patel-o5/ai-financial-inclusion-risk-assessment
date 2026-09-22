# rag/retriever.py

import json
import sqlite3
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# ─── CONFIG ───────────────────────────────────────────
DB_PATH = Path(__file__).resolve().parent / "reg_chunks.db"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# ─── FEATURE → DUAL-LANE MAPPING (14 TARGET CHUNKS) ───

FEATURE_METADATA = {
    # ── Payment History ──
    "late_payment_share": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of delinquency frequency, late payment share, and historical installment repayment records.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "mean_days_late": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of average delinquency duration and timeliness of previous payments.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "max_days_late": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes evaluation of maximum days past due and severe delinquency events.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },
    "underpayment_share": {
        "standard_category": "Delinquent past or present credit obligations with others",
        "form_c1_item": "Part I (Item 15): Delinquent past or present credit obligations with others",
        "statutory_scope": "Authorizes consideration of partial payments, payment amounts, and installment shortfall records.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "interp_9_b2_comment4",
    },

    # ── Income & Debt Ratios ──
    "credit_income_ratio": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes consideration of requested loan size relative to income amount and debt service capacity.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "annuity_income_ratio": {
        "standard_category": "Excessive obligations in relation to income",
        "form_c1_item": "Part I (Item 9): Excessive obligations in relation to income",
        "statutory_scope": "Authorizes evaluation of recurring debt burden and annuity continuity relative to total income.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_CREDIT": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes evaluation of total credit requested against applicant earnings and repayment ability.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_INCOME_TOTAL": {
        "standard_category": "Income insufficient for amount of credit requested",
        "form_c1_item": "Part I (Item 8): Income insufficient for amount of credit requested",
        "statutory_scope": "Authorizes evaluation of total verified income amount and probable continuance.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "AMT_ANNUITY": {
        "standard_category": "Excessive obligations in relation to income",
        "form_c1_item": "Part I (Item 9): Excessive obligations in relation to income",
        "statutory_scope": "Authorizes evaluation of annual payment obligations relative to income flow.",
        "lane_1_id": "regb_1002_6_b_5",
        "lane_2_id": "regb_1002_9_b_2",
    },

    # ── Employment & Profile ──
    "employment_years": {
        "standard_category": "Length of employment",
        "form_c1_item": "Part I (Item 7): Length of employment",
        "statutory_scope": "Authorizes evaluation of employment duration, tenure stability, and job continuity.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "interp_9_b2_comment2",
    },
    "NAME_INCOME_TYPE": {
        "standard_category": "Temporary or irregular employment",
        "form_c1_item": "Part I (Item 5): Temporary or irregular employment",
        "statutory_scope": "Authorizes evaluation of employment type stability and ongoing income stream characteristics.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "interp_9_b2_comment2",
    },
    "NAME_EDUCATION_TYPE": {
        "standard_category": "Applicant creditworthiness profile",
        "form_c1_item": "Part I (Item 23): Other pertinent credit evaluation factors",
        "statutory_scope": "Authorizes consideration of pertinent background information not on prohibited bases.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "regb_1002_9_b_2",
    },
    "NAME_HOUSING_TYPE": {
        "standard_category": "Length or stability of residence",
        "form_c1_item": "Part I (Item 10): Length of residence / living arrangements",
        "statutory_scope": "Authorizes consideration of residence stability and housing obligations.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "regb_1002_9_b_2",
    },

    # ── Thin-File / Alternative Data ──
    "thin_file": {
        "standard_category": "No credit file / Limited credit experience",
        "form_c1_item": "Part I (Item 13 & 14): No credit file / Limited credit experience",
        "statutory_scope": "Authorizes consideration of breadth and depth of applicant credit records and alternative data.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2022_03_response",
    },
    "mobile_bill_consistency": {
        "standard_category": "Insufficient alternative credit references",
        "form_c1_item": "Part I (Item 2): Insufficient number of credit references provided",
        "statutory_scope": "Authorizes evaluation of recurring non-traditional utility/telecom cash flow payment consistency.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2022_03_response",
    },

    # ── Credit Accounts / Installments ──
    "bureau_active_credits_count": {
        "standard_category": "Insufficient number of credit references provided",
        "form_c1_item": "Part I (Item 2): Insufficient number of credit references provided",
        "statutory_scope": "Authorizes evaluation of the number and depth of verified active credit reference accounts.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "circular_2023_03_response",
    },
    "installments_count": {
        "standard_category": "Limited installment credit experience",
        "form_c1_item": "Part I (Item 14): Limited credit experience",
        "statutory_scope": "Authorizes evaluation of past installment loan volume, experience, and trade line maturity.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "circular_2023_03_response",
    },

    # ── Prior Refusals & Inquiries ──
    "prev_refusal_rate": {
        "standard_category": "Poor credit performance / previous credit denial history",
        "form_c1_item": "Part I (Item 15): Poor credit performance with others / prior credit history",
        "statutory_scope": "Authorizes consideration of prior bureau credit history, credit inquiry frequency, and past credit decisions.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "fcra_1681m_a_1_2",
    },
    "prev_refused_count": {
        "standard_category": "Poor credit performance / previous credit denial history",
        "form_c1_item": "Part I (Item 15): Poor credit performance with others / prior credit history",
        "statutory_scope": "Authorizes consideration of prior bureau credit history and refusal counts.",
        "lane_1_id": "regb_1002_6_b_6",
        "lane_2_id": "fcra_1681m_a_1_2",
    },
    "prev_applications_count": {
        "standard_category": "Number of recent inquiries on credit bureau report",
        "form_c1_item": "Part I (Item 21): Number of recent inquiries on credit bureau report",
        "statutory_scope": "Authorizes consideration of recent credit application inquiry volume and bureau report activity.",
        "lane_1_id": "regb_1002_6_a",
        "lane_2_id": "fcra_1681m_a_3_4",
    },
}

FEATURE_TO_CLAUSE = {
    fname: meta["lane_1_id"] for fname, meta in FEATURE_METADATA.items()
}


# ─── STEP 1: EXACT LOOKUP ─────────────────────────────
def lookup_by_clause_id(clause_id: str) -> dict | None:
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT chunk_id, citation, chunk_type, text FROM reg_chunks WHERE chunk_id = ?",
        (clause_id,)
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "chunk_id":   row[0],
        "citation":   row[1],
        "chunk_type": row[2],
        "text":       row[3],
        "similarity": 1.0,
    }


# ─── STEP 2: VECTOR SEARCH ────────────────────────────
def vector_search(query: str, top_k: int = 5) -> list[dict]:
    query_vec = EMBED_MODEL.encode(query).tolist()

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()
    cur.execute(
        "SELECT chunk_id, citation, chunk_type, text, embedding FROM reg_chunks"
    )
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        chunk_id, citation, chunk_type, text, emb_blob = row
        emb = np.array(json.loads(emb_blob), dtype=np.float32)
        sim = float(
            np.dot(query_vec, emb) /
            (np.linalg.norm(query_vec) * np.linalg.norm(emb) + 1e-9)
        )
        results.append({
            "chunk_id":   chunk_id,
            "citation":   citation,
            "chunk_type": chunk_type,
            "text":       text,
            "similarity": sim,
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


# ─── STEP 3: DEDUPLICATE ──────────────────────────────
def deduplicate(chunks: list[dict]) -> list[dict]:
    seen = {}
    for chunk in chunks:
        cid = chunk["chunk_id"]
        if cid not in seen or chunk["similarity"] > seen[cid]["similarity"]:
            seen[cid] = chunk
    return list(seen.values())


# ─── STEP 4: MASTER RETRIEVE FUNCTION ────────────────
def retrieve(
    shap_features: list[dict],
    decision_band: str,
    is_thin_file: bool,
    applicant_id: str
) -> dict:

    raw_chunks = []
    pinned_ids = set()

    for feat in shap_features:
        fname = feat["feature_name"]
        meta = FEATURE_METADATA.get(fname, {
            "standard_category": "Credit application evaluation factor",
            "lane_1_id": "regb_1002_6_a",
            "lane_2_id": "regb_1002_9_b_2",
        })

        # Pin both Lane 1 and Lane 2 clauses
        for cid in [meta["lane_1_id"], meta["lane_2_id"]]:
            exact = lookup_by_clause_id(cid)
            if exact:
                raw_chunks.append(exact)
                pinned_ids.add(cid)

        # Vector search fallback
        vec_results = vector_search(
            query=f"adverse action reason disclosure requirement for {fname}",
            top_k=2
        )
        raw_chunks.extend(vec_results)

    # deduplicate
    deduped = deduplicate(raw_chunks)

    # Sort with pinned clauses first, then by similarity
    ranked = sorted(
        deduped,
        key=lambda x: (1.0 if x["chunk_id"] in pinned_ids else 0.5, x["similarity"]),
        reverse=True
    )

    return {
        "applicant_id": applicant_id,
        "retrieved_clauses": [
            {
                "chunk_id":    c["chunk_id"],
                "citation":    c["citation"],
                "chunk_type":  c["chunk_type"],
                "text":        c["text"],
                "similarity":  c["similarity"],
                "final_score": 1.0 if c["chunk_id"] in pinned_ids else round(c["similarity"], 4),
            }
            for c in ranked
        ]
    }


if __name__ == "__main__":
    mock_shap = [
        {"feature_name": "late_payment_share", "value": 0.35, "shap": 0.42},
        {"feature_name": "credit_income_ratio", "value": 5.8, "shap": 0.31},
        {"feature_name": "thin_file", "value": 1.0, "shap": 0.22},
        {"feature_name": "installments_count", "value": 4.0, "shap": 0.15},
    ]

    res = retrieve(
        shap_features=mock_shap,
        decision_band="Deny",
        is_thin_file=True,
        applicant_id="TEST_001",
    )

    print(f"Retrieved {len(res['retrieved_clauses'])} clauses for {res['applicant_id']}:")
    for cl in res["retrieved_clauses"]:
        print(f"  - {cl['chunk_id']:<32} | {cl['citation']:<30} | score: {cl['final_score']}")