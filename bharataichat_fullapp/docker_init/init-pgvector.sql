CREATE EXTENSION IF NOT EXISTS pgvector;
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    content TEXT,
    metadata JSONB,
    embedding vector(384)
);
