"""
Embedding & Vector Storage Pipeline for Regulated-Lending RAG System (SQLite-only).

1. Loads chunks.json (from rag/chunks.json or corpus/chunks.json).
2. Embeds each chunk's text using sentence-transformers (all-MiniLM-L6-v2, 384 dimensions).
3. Initializes local SQLite vector store (rag/reg_chunks.db).
4. Upserts all chunks idempotently (INSERT OR REPLACE).
5. Runs sanity query (5 regulation chunks) and tests lookup_by_clause_id("regb_1002_9_b_2").
"""

import json
import sqlite3
import sys
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


def init_sqlite_db(db_path: Path):
    """Initialize local SQLite database as vector store."""
    conn = sqlite3.connect(db_path)
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reg_chunks (
                chunk_id       TEXT PRIMARY KEY,
                source_doc     TEXT NOT NULL,
                citation       TEXT NOT NULL,
                parent_section TEXT,
                heading        TEXT,
                chunk_type     TEXT NOT NULL,
                text           TEXT NOT NULL,
                page_hint      INTEGER,
                embedding      TEXT NOT NULL
            );
            """
        )
    return conn


def load_chunks(base_dir: Path) -> list[dict]:
    """Load chunks.json from rag/ or corpus/ directory."""
    paths_to_try = [
        base_dir / "rag" / "chunks.json",
        base_dir / "corpus" / "chunks.json",
    ]
    for p in paths_to_try:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)

    raise FileNotFoundError(f"chunks.json not found in any of: {paths_to_try}")


def embed_chunks(chunks: list[dict], batch_size: int = 32) -> list[np.ndarray]:
    """Embed all chunk texts using all-MiniLM-L6-v2."""
    print("Loading embedding model: all-MiniLM-L6-v2...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    texts = [ch["text"] for ch in chunks]
    total = len(texts)
    embeddings = []

    print(f"Embedding {total} chunks in batches of {batch_size}...")
    for i in range(0, total, batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_embeddings = model.encode(batch_texts, show_progress_bar=False)
        embeddings.extend(batch_embeddings)

        processed = min(i + batch_size, total)
        if processed % 20 == 0 or processed == total:
            print(f"  Progress: Embedded {processed}/{total} chunks ({(processed / total):.1%})")

    return embeddings


def upsert_sqlite(conn, chunks: list[dict], embeddings: list[np.ndarray]):
    """Upsert chunks into local SQLite database."""
    records = []
    for ch, emb in zip(chunks, embeddings):
        records.append(
            (
                ch["chunk_id"],
                ch["source_doc"],
                ch["citation"],
                ch.get("parent_section"),
                ch.get("heading"),
                ch["chunk_type"],
                ch["text"],
                ch.get("page_hint"),
                json.dumps(emb.tolist()),
            )
        )

    sql = """
        INSERT OR REPLACE INTO reg_chunks (
            chunk_id, source_doc, citation, parent_section, heading,
            chunk_type, text, page_hint, embedding
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    with conn:
        conn.executemany(sql, records)


def lookup_by_clause_id(clause_id: str, conn) -> dict | None:
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT chunk_id, source_doc, citation, parent_section,
               heading, chunk_type, text, page_hint
        FROM reg_chunks
        WHERE chunk_id = ?;
        """,
        (clause_id,),
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {
        "chunk_id": row[0],
        "source_doc": row[1],
        "citation": row[2],
        "parent_section": row[3],
        "heading": row[4],
        "chunk_type": row[5],
        "text": row[6],
        "page_hint": row[7],
    }


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent

    print("=" * 80)
    print("REGULATED LENDING RAG — EMBED & LOAD TO SQLITE VECTOR STORE")
    print("=" * 80)

    # 1. Load chunks
    chunks = load_chunks(base_dir)
    print(f"Loaded {len(chunks)} chunks from chunks.json.")

    # 2. Embed chunks
    embeddings = embed_chunks(chunks, batch_size=32)
    print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}.")

    # 3. Connect to SQLite
    sqlite_path = base_dir / "rag" / "reg_chunks.db"
    conn = init_sqlite_db(sqlite_path)
    print(f"\nInitialized local SQLite vector store: {sqlite_path}")

    # 4. Upsert all chunks
    upsert_sqlite(conn, chunks, embeddings)
    print(f"Upserted {len(chunks)} chunks into reg_chunks table.")

    # 5. Sanity count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM reg_chunks;")
    total_rows = cursor.fetchone()[0]
    print(f"\nTotal rows in reg_chunks table: {total_rows}")

    # 6. Sanity query — 5 regulation chunks
    print("\nSanity Query Results (5 'regulation' chunks):")
    cursor.execute(
        """
        SELECT chunk_id, citation
        FROM reg_chunks
        WHERE chunk_type = 'regulation'
        ORDER BY chunk_id
        LIMIT 5;
        """
    )
    rows = cursor.fetchall()
    print(f"{'chunk_id':30s} | {'citation':s}")
    print("-" * 65)
    for r in rows:
        print(f"{r[0]:30s} | {r[1]:s}")

    # 7. Test lookup
    test_clause = "regb_1002_9_b_2"
    print(f"\n{'=' * 80}")
    print(f"TESTING lookup_by_clause_id('{test_clause}')")
    print("=" * 80)
    clause_data = lookup_by_clause_id(test_clause, conn=conn)

    if clause_data:
        print(f"Chunk ID       : {clause_data['chunk_id']}")
        print(f"Source Doc     : {clause_data['source_doc']}")
        print(f"Citation       : {clause_data['citation']}")
        print(f"Parent Section : {clause_data['parent_section']}")
        print(f"Heading        : {clause_data['heading']}")
        print(f"Chunk Type     : {clause_data['chunk_type']}")
        print(f"Page Hint      : {clause_data['page_hint']}")
        print(f"Text:\n{clause_data['text']}")
    else:
        print(f"Error: Clause {test_clause} not found.")

    conn.close()
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
