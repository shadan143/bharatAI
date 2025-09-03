# Simple pgvector-backed vector store wrapper. This expects a Postgres with pgvector extension
# and a table "documents(id text primary key, content text, embedding vector)".
import os, json
from sqlalchemy import text
from .db import engine

def ensure_table():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            content TEXT,
            metadata JSONB,
            embedding vector(384)
        );
        """))
ensure_table()

def upsert_document(doc_id, content, embedding, metadata=None):
    sql = text("""
    INSERT INTO documents (id, content, metadata, embedding)
    VALUES (:id, :content, :metadata, :emb)
    ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, metadata = EXCLUDED.metadata, embedding = EXCLUDED.embedding;
    """)
    with engine.connect() as conn:
        conn.execute(sql, {"id": doc_id, "content": content, "metadata": json.dumps(metadata or {}), "emb": embedding})

def search_similar(embedding, top_k=3):
    # Uses pgvector's <-> operator for cosine distance
    with engine.connect() as conn:
        res = conn.execute(text("""
            SELECT id, content, metadata FROM documents
            ORDER BY embedding <-> :emb
            LIMIT :k
        """), {"emb": embedding, "k": top_k})
        rows = [{"id": r[0], "content": r[1], "metadata": r[2]} for r in res.fetchall()]
        return rows
