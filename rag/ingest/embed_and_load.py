"""
Embedding & Vector Storage Pipeline for Regulated-Lending RAG System.

1. Loads chunks.json (from rag/chunks.json or corpus/chunks.json).
2. Embeds each chunk's text using sentence-transformers (all-MiniLM-L6-v2, 384 dimensions).
3. Reads PostgreSQL env vars from .env: PG_HOST, PG_PORT, PG_DB, PG_USER, PG_PASS.
4. If PostgreSQL is reachable, initializes pgvector extension, reg_chunks table, and IVFFlat index.
   If PostgreSQL is unavailable, gracefully falls back to local SQLite vector store (rag/reg_chunks.db).
5. Upserts all chunks idempotently (ON CONFLICT / REPLACE).
6. Runs sanity query (5 regulation chunks) and tests lookup_by_clause_id("regb_1002_9_b_2").
"""

import json
import os
import sqlite3
import sys
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer

# Try importing dotenv
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try importing psycopg2 & pgvector
try:
    import psycopg2
    from psycopg2.extras import execute_values
    from pgvector.psycopg2 import register_vector
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False


def get_pg_connection():
    """Attempt PostgreSQL connection using environment variables."""
    required_vars = ["PG_HOST", "PG_PORT", "PG_DB", "PG_USER", "PG_PASS"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    if missing:
        return None

    if not HAS_PSYCOPG2:
        return None

    try:
        conn = psycopg2.connect(
            host=os.environ["PG_HOST"],
            port=int(os.environ["PG_PORT"]),
            dbname=os.environ["PG_DB"],
            user=os.environ["PG_USER"],
            password=os.environ["PG_PASS"],
            connect_timeout=3,
        )
        return conn
    except Exception:
        return None


def init_sqlite_db(db_path: Path):
    """Initialize local SQLite database as fallback vector store."""
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


def init_pg_db(conn):
    """Enable pgvector extension, create reg_chunks table, and create IVFFlat index."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        register_vector(conn)
        cur.execute(
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
                embedding      vector(384)
            );
            """
        )
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS reg_chunks_embedding_idx
            ON reg_chunks
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 20);
            """
        )
    conn.commit()


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


def upsert_pg(conn, chunks: list[dict], embeddings: list[np.ndarray]):
    """Upsert chunks into PostgreSQL with pgvector."""
    register_vector(conn)
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
                emb.tolist(),
            )
        )

    upsert_sql = """
        INSERT INTO reg_chunks (
            chunk_id, source_doc, citation, parent_section, heading,
            chunk_type, text, page_hint, embedding
        )
        VALUES %s
        ON CONFLICT (chunk_id) DO UPDATE SET
            source_doc     = EXCLUDED.source_doc,
            citation       = EXCLUDED.citation,
            parent_section = EXCLUDED.parent_section,
            heading        = EXCLUDED.heading,
            chunk_type     = EXCLUDED.chunk_type,
            text           = EXCLUDED.text,
            page_hint      = EXCLUDED.page_hint,
            embedding      = EXCLUDED.embedding;
    """
    with conn.cursor() as cur:
        execute_values(cur, upsert_sql, records, page_size=100)
    conn.commit()


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


def lookup_by_clause_id(clause_id: str, mode: str, conn) -> dict | None:
    """Primary retrieval path at inference time: lookup a regulatory chunk by exact chunk_id."""
    if mode == "pg":
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT chunk_id, source_doc, citation, parent_section,
                       heading, chunk_type, text, page_hint
                FROM reg_chunks
                WHERE chunk_id = %s;
                """,
                (clause_id,),
            )
            row = cur.fetchone()
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
    else:
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
    print("REGULATED LENDING RAG — EMBED & LOAD TO VECTOR DATABASE")
    print("=" * 80)

    # 1. Load chunks
    chunks = load_chunks(base_dir)
    print(f"Loaded {len(chunks)} chunks from chunks.json.")

    # 2. Embed chunks
    embeddings = embed_chunks(chunks, batch_size=32)
    print(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0])}.")

    # 3. Connect to DB (PostgreSQL or local SQLite fallback)
    pg_conn = get_pg_connection()

    if pg_conn:
        mode = "pg"
        conn = pg_conn
        print("\nConnected to live PostgreSQL database with pgvector.")
        init_pg_db(conn)
        upsert_pg(conn, chunks, embeddings)
    else:
        mode = "sqlite"
        sqlite_path = base_dir / "rag" / "reg_chunks.db"
        conn = init_sqlite_db(sqlite_path)
        print(f"\nPostgreSQL offline/unreachable. Initialized local vector store: {sqlite_path}")
        upsert_sqlite(conn, chunks, embeddings)

    # 4. Print total count & 5 regulation chunks sanity query
    if mode == "pg":
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM reg_chunks;")
            total_rows = cur.fetchone()[0]
            print(f"\nTotal rows in reg_chunks table: {total_rows}")

            print("\nSanity Query Results (5 'regulation' chunks):")
            cur.execute(
                """
                SELECT chunk_id, citation
                FROM reg_chunks
                WHERE chunk_type = 'regulation'
                ORDER BY chunk_id
                LIMIT 5;
                """
            )
            rows = cur.fetchall()
    else:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reg_chunks;")
        total_rows = cursor.fetchone()[0]
        print(f"\nTotal rows in reg_chunks table: {total_rows}")

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

    # 5. Test lookup_by_clause_id
    test_clause = "regb_1002_9_b_2"
    print(f"\n" + "=" * 80)
    print(f"TESTING lookup_by_clause_id('{test_clause}')")
    print("=" * 80)
    clause_data = lookup_by_clause_id(test_clause, mode=mode, conn=conn)

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
        print(f"Error: Clause {test_clause} not found in database.")

    conn.close()
    print("\n" + "=" * 80)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    main()
