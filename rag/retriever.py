# rag/retriever.py

import json
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

# ─── CONFIG ───────────────────────────────────────────
DB_PATH = "rag/reg_chunks.db"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# ─── RERANKING WEIGHTS ────────────────────────────────
TYPE_WEIGHT = {
    "regulation": 1.0,
    "commentary": 0.85,
    "circular":   0.80,
    "form":       0.40
}

DENY_BOOST_IDS = [
    "regb_1002_9_b_2",
    "circular_2023_03_analysis_p3",
    "fcra_1681m_a"
]

THIN_FILE_BOOST_IDS = [
    "circular_2022_03_analysis_p1",
    "circular_2023_03_analysis_p3"
]


# ─── STEP 1: EXACT LOOKUP ─────────────────────────────
def lookup_by_clause_id(clause_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
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
        "similarity": 1.0      # exact match gets perfect similarity
    }


# ─── STEP 2: VECTOR SEARCH ────────────────────────────
def vector_search(query: str, top_k: int = 5) -> list[dict]:
    query_vec = EMBED_MODEL.encode(query).tolist()

    conn = sqlite3.connect(DB_PATH)
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
        # cosine similarity
        sim = float(
            np.dot(query_vec, emb) /
            (np.linalg.norm(query_vec) * np.linalg.norm(emb) + 1e-9)
        )
        results.append({
            "chunk_id":   chunk_id,
            "citation":   citation,
            "chunk_type": chunk_type,
            "text":       text,
            "similarity": sim
        })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:top_k]


# ─── STEP 3: DEDUPLICATE ──────────────────────────────
def deduplicate(chunks: list[dict]) -> list[dict]:
    seen = {}
    for chunk in chunks:
        cid = chunk["chunk_id"]
        # keep highest similarity if duplicate
        if cid not in seen or chunk["similarity"] > seen[cid]["similarity"]:
            seen[cid] = chunk
    return list(seen.values())


# ─── STEP 4: RERANK ───────────────────────────────────
def rerank_chunks(
    chunks: list[dict],
    decision_band: str,
    is_thin_file: bool
) -> list[dict]:

    scored = []
    for chunk in chunks:
        score = chunk["similarity"]
        score *= TYPE_WEIGHT.get(chunk["chunk_type"], 0.7)

        if decision_band == "Deny" and chunk["chunk_id"] in DENY_BOOST_IDS:
            score *= 1.20

        if is_thin_file and chunk["chunk_id"] in THIN_FILE_BOOST_IDS:
            score *= 1.15

        scored.append({**chunk, "final_score": round(score, 4)})

    scored.sort(key=lambda x: x["final_score"], reverse=True)
    return scored[:4]


# ─── STEP 5: MASTER RETRIEVE FUNCTION ────────────────
def retrieve(
    shap_features: list[dict],   # from ML pipeline
    decision_band: str,          # "Approve" | "Refer" | "Deny"
    is_thin_file: bool,
    applicant_id: str
) -> dict:
    """
    shap_features format:
    [
      {"feature_name": "late_payment_share", "value": 0.35, "shap": 0.142},
      {"feature_name": "prev_refusal_rate",  "value": 0.82, "shap": 0.118},
      {"feature_name": "mean_days_late",     "value": 12.0, "shap": 0.095}
    ]
    """

    raw_chunks = []

    for feat in shap_features:
        fname = feat["feature_name"]

        # 1. exact lookup using hardcoded feature→clause mapping
        clause_id = FEATURE_TO_CLAUSE.get(fname)
        if clause_id:
            exact = lookup_by_clause_id(clause_id)
            if exact:
                raw_chunks.append(exact)

        # 2. vector search using feature name as query
        vec_results = vector_search(
            query=f"adverse action reason disclosure requirement for {fname}",
            top_k=3
        )
        raw_chunks.extend(vec_results)

    # 3. deduplicate
    deduped = deduplicate(raw_chunks)

    # 4. rerank
    ranked = rerank_chunks(deduped, decision_band, is_thin_file)

    # 5. handoff dict — this is what generator.py receives
    return {
        "applicant_id": applicant_id,
        "retrieved_clauses": [
            {
                "chunk_id":    c["chunk_id"],
                "citation":    c["citation"],
                "chunk_type":  c["chunk_type"],
                "text":        c["text"],
                "similarity":  c["similarity"],
                "final_score": c["final_score"]
            }
            for c in ranked
        ]
    }


# ─── FEATURE → CLAUSE MAPPING ─────────────────────────
# No LLM needed. Deterministic map of your 17 features
# to their primary regulatory clause.
FEATURE_TO_CLAUSE = {
    "late_payment_share":       "regb_1002_9_b_2",
    "mean_days_late":           "regb_1002_9_b_2",
    "max_days_late":            "regb_1002_9_b_2",
    "underpayment_share":       "regb_1002_9_b_2",
    "installments_count":       "circular_2023_03_analysis_p3",
    "prev_refused_count":       "fcra_1681m_a",
    "prev_refusal_rate":        "fcra_1681m_a",
    "prev_applications_count":  "fcra_1681m_a",
    "credit_income_ratio":      "regb_1002_9_b_2",
    "annuity_income_ratio":     "regb_1002_9_b_2",
    "AMT_INCOME_TOTAL":         "regb_1002_9_b_2",
    "AMT_CREDIT":               "regb_1002_9_b_2",
    "AMT_ANNUITY":              "regb_1002_9_b_2",
    "employment_years":         "regb_1002_9_b_2",
    "mobile_bill_consistency":  "circular_2022_03_analysis_p1",
    "thin_file":                "circular_2022_03_analysis_p1",
    "NAME_EDUCATION_TYPE":      "regb_1002_9_b_2",
    "NAME_INCOME_TYPE":         "regb_1002_9_b_2",
    "NAME_HOUSING_TYPE":        "regb_1002_9_b_2",
}

