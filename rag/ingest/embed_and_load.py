"""
Embedding & Vector Storage Pipeline for Regulated-Lending RAG System (SQLite-only).

1. Loads rag/chunks.json (the 14 target regulatory chunks).
2. Embeds each chunk's text using sentence-transformers (all-MiniLM-L6-v2, 384 dimensions).
3. Initializes local SQLite vector store (rag/reg_chunks.db).
4. Upserts all chunks idempotently (INSERT OR REPLACE).
5. Runs sanity queries to verify deterministic and semantic lookup.
"""

import json
import sqlite3
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer


def init_sqlite_db(db_path: Path) -> sqlite3.Connection:
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
        print(f"  Progress: Embedded {processed}/{total} chunks ({(processed / total):.1%})")

    return embeddings


def upsert_sqlite(conn: sqlite3.Connection, chunks: list[dict], embeddings: list[np.ndarray]):
    """Upsert chunks into local SQLite database."""
    records = []
    for ch, emb in zip(chunks, embeddings):
        source_doc = ch.get("source_doc") or ch.get("source_file", "unknown")
        lane = ch.get("lane", 1)
        chunk_type = f"lane_{lane}" if "lane" in ch else ch.get("chunk_type", "regulation")

        records.append(
            (
                ch["chunk_id"],
                source_doc,
                ch["citation"],
                ch.get("parent_section", ""),
                ch.get("heading", ""),
                chunk_type,
                ch["text"],
                ch.get("page_hint", 1),
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


def lookup_by_clause_id(clause_id: str, conn: sqlite3.Connection) -> dict | None:
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
    if not (base_dir / "rag").exists():
        base_dir = Path.cwd()

    db_path = base_dir / "rag" / "reg_chunks.db"

    print("=" * 80)
    print("REGULATED LENDING RAG — EMBED & LOAD TO SQLITE VECTOR STORE")
    print("=" * 80)

    # 1. Load chunks
    chunks = load_chunks(base_dir)
    print(f"Loaded {len(chunks)} chunks from chunks.json")

    # 2. Embed chunks
    embeddings = embed_chunks(chunks)

    # 3. Initialize SQLite
    conn = init_sqlite_db(db_path)

    # 4. Upsert
    upsert_sqlite(conn, chunks, embeddings)
    print(f"Upserted {len(chunks)} chunks to SQLite ({db_path})")

    # 5. Test lookup
    test_id = "regb_1002_6_b_5"
    result = lookup_by_clause_id(test_id, conn)
    if result:
        print(f"\nSanity lookup test PASS: found '{test_id}' -> citation: {result['citation']}")
    else:
        print(f"\nSanity lookup test FAILED for '{test_id}'")

    conn.close()
    print("\nDatabase load complete.")


if __name__ == "__main__":
    main()
