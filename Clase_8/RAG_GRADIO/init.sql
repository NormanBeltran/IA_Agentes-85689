-- Habilita la extensión pgvector en la base.
CREATE EXTENSION IF NOT EXISTS vector;

-- Cada fila representa un fragmento (chunk) de un documento.
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,

    -- El modelo paraphrase-multilingual-MiniLM-L12-v2 genera 384 dimensiones.
    embedding VECTOR(384) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Evita duplicar un mismo chunk del mismo archivo.
CREATE UNIQUE INDEX IF NOT EXISTS idx_documents_file_chunk
ON documents(filename, chunk_index);

-- Índice vectorial para acelerar consultas por similitud coseno.
CREATE INDEX IF NOT EXISTS idx_documents_embedding_hnsw
ON documents
USING hnsw (embedding vector_cosine_ops);