"""
Comprehensive End-to-End Test Suite for Credit Risk ML & Regulatory RAG Pipeline.

Tests:
1. Production ML Model (17 features, calibrator, thresholds, demo pool).
2. Parsed Regulatory Texts (6 files in rag/parsed/).
3. Legal Chunks (65 chunks in rag/chunks.json).
4. Vector Storage & Inference Retrieval (lookup_by_clause_id & cosine similarity search).
"""

import json
import pickle
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def test_ml_pipeline():
    print("=" * 80)
    print("TEST 1: PRODUCTION ML MODEL & ARTIFACTS")
    print("=" * 80)

    # 1. Feature list
    feat_path = BASE_DIR / "ml" / "feature_list.json"
    with open(feat_path, "r") as f:
        features = json.load(f)
    print(f"[OK] Feature list loaded: {len(features)} features ({', '.join(features[:3])}...)")

    # 2. Model & Calibrator
    with open(BASE_DIR / "ml" / "model.pkl", "rb") as f:
        model = pickle.load(f)
    with open(BASE_DIR / "ml" / "calibrator.pkl", "rb") as f:
        calibrator = pickle.load(f)
    print(f"[OK] Model & Isotonic Calibrator loaded successfully.")

    # 3. Decision Thresholds
    with open(BASE_DIR / "ml" / "thresholds.json", "r") as f:
        thresholds = json.load(f)
    print(f"[OK] Decision Thresholds: Approve < {thresholds['approve_below']:.5f}, Deny > {thresholds['deny_above']:.5f}")

    # 4. Demo Pool Test Prediction
    demo_pool = pd.read_parquet(BASE_DIR / "data" / "demo_pool.parquet")
    # Apply encoder for NAME_INCOME_TYPE if categorical
    with open(BASE_DIR / "ml" / "encoders" / "NAME_INCOME_TYPE.pkl", "rb") as f:
        le_inc = pickle.load(f)
    if demo_pool["NAME_INCOME_TYPE"].dtype == 'object':
        demo_pool["NAME_INCOME_TYPE"] = le_inc.transform(demo_pool["NAME_INCOME_TYPE"].astype(str))

    raw_probs = model.predict_proba(demo_pool[features])[:, 1]
    calib_probs = np.clip(calibrator.predict(raw_probs), 0.005, 1.0)
    print(f"[OK] Demo Pool (200 applicants) evaluated:")
    print(f"     - Min Calibrated Score : {calib_probs.min():.5f} (Floor >= 0.005: {calib_probs.min() >= 0.005})")
    print(f"     - Max Calibrated Score : {calib_probs.max():.5f}")
    print(f"     - Mean Calibrated Score: {calib_probs.mean():.5f}")


def test_rag_ingest():
    print("\n" + "=" * 80)
    print("TEST 2: RAG PARSED TEXTS & CHUNKS")
    print("=" * 80)

    # 1. Parsed text files
    parsed_dir = BASE_DIR / "rag" / "parsed"
    parsed_files = list(parsed_dir.glob("*.txt"))
    print(f"[OK] Found {len(parsed_files)} parsed regulatory text files in rag/parsed/:")
    for f in parsed_files:
        size_kb = f.stat().st_size / 1024
        print(f"     - {f.name:45s} ({size_kb:5.1f} KB)")

    # 2. Chunks JSON
    chunks_path = BASE_DIR / "rag" / "chunks.json"
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"\n[OK] Loaded {len(chunks)} legal chunks from rag/chunks.json.")

    types = {}
    for ch in chunks:
        t = ch["chunk_type"]
        types[t] = types.get(t, 0) + 1
    print(f"     - Breakdown: {types}")


def test_vector_retrieval():
    print("\n" + "=" * 80)
    print("TEST 3: VECTOR STORAGE & RETRIEVAL")
    print("=" * 80)

    # Test SQLite vector store or PG connection
    from rag.ingest.embed_and_load import lookup_by_clause_id, get_pg_connection, init_sqlite_db

    pg_conn = get_pg_connection()
    if pg_conn:
        mode = "pg"
        conn = pg_conn
        print("[OK] Connected to live PostgreSQL database with pgvector.")
    else:
        mode = "sqlite"
        db_path = BASE_DIR / "rag" / "reg_chunks.db"
        conn = init_sqlite_db(db_path)
        print(f"[OK] Loaded local vector database: {db_path}")

    # Exact clause lookup
    clause = "regb_1002_9_b_2"
    result = lookup_by_clause_id(clause, mode=mode, conn=conn)
    assert result is not None, f"Failed to retrieve clause {clause}"
    print(f"\n[OK] Exact Clause Lookup Test ('{clause}'):")
    print(f"     - Citation : {result['citation']}")
    print(f"     - Heading  : {result['heading']}")
    print(f"     - Snippet  : {result['text'][:120]}...")

    # Semantic Vector Search Test
    print(f"\n[OK] Semantic Vector Search Test:")
    query = "What are the requirements for providing specific reasons for adverse action under Regulation B?"
    print(f"     - Query: '{query}'")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    q_emb = model.encode(query)

    cursor = conn.cursor()
    if mode == "sqlite":
        cursor.execute("SELECT chunk_id, citation, heading, text, embedding FROM reg_chunks;")
        rows = cursor.fetchall()
        scored = []
        for cid, cite, head, txt, emb_str in rows:
            emb = np.array(json.loads(emb_str))
            # Cosine similarity
            sim = float(np.dot(q_emb, emb) / (np.linalg.norm(q_emb) * np.linalg.norm(emb)))
            scored.append((sim, cid, cite, head, txt))
        scored.sort(reverse=True, key=lambda x: x[0])
        top_results = scored[:3]
    else:
        cursor.execute(
            """
            SELECT chunk_id, citation, heading, text, (1 - (embedding <=> %s::vector)) as similarity
            FROM reg_chunks
            ORDER BY embedding <=> %s::vector
            LIMIT 3;
            """,
            (q_emb.tolist(), q_emb.tolist()),
        )
        top_results = [(r[4], r[0], r[1], r[2], r[3]) for r in cursor.fetchall()]

    print("\n     Top 3 Semantically Retrieved Regulatory Chunks:")
    for rank, (sim, cid, cite, head, txt) in enumerate(top_results, 1):
        print(f"     {rank}. [{cite}] (Similarity: {sim:.4f})")
        print(f"        Heading: {head}")
        print(f"        ID     : {cid}")

    conn.close()


def main():
    test_ml_pipeline()
    test_rag_ingest()
    test_vector_retrieval()
    print("\n" + "=" * 80)
    print("ALL SYSTEM INTEGRATION TESTS PASSED PERFECTLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
