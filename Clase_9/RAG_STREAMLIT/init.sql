-- ============================================================
-- RAG - Inicialización de PostgreSQL + pgvector
-- ============================================================

-- Habilitar la extensión vector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de fragmentos de documentos
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,

    -- El modelo paraphrase-multilingual-MiniLM-L12-v2
    -- genera embeddings de 384 dimensiones.
    embedding VECTOR(384),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice HNSW para acelerar las búsquedas por similitud coseno
CREATE INDEX IF NOT EXISTS documents_embedding_hnsw
ON documents
USING hnsw (embedding vector_cosine_ops);

-- Evita chunks duplicados de un mismo archivo
CREATE UNIQUE INDEX IF NOT EXISTS documents_file_chunk
ON documents(filename, chunk_index);