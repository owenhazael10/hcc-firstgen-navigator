-- HC First-Gen Navigator Database Schema
-- Supabase PostgreSQL with pgvector for RAG

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Conversations table - logs all chat interactions
CREATE TABLE IF NOT EXISTS conversations (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at timestamp DEFAULT now(),
  user_message text,
  agent_response text,
  feedback text,
  language text
);

-- HC Documents table - stores document chunks with embeddings for RAG
CREATE TABLE IF NOT EXISTS hc_documents (
  id bigserial PRIMARY KEY,
  source text NOT NULL,
  section text,
  content text NOT NULL,
  embedding vector(1024),
  created_at timestamp DEFAULT now()
);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS hc_documents_embedding_idx 
ON hc_documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Function to search documents by semantic similarity
CREATE OR REPLACE FUNCTION match_hc_documents (
  query_embedding vector(1024),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 5
) RETURNS TABLE (
  id bigint,
  source text,
  section text,
  content text,
  similarity float
) LANGUAGE plpgsql AS $$
BEGIN
  RETURN QUERY
  SELECT 
    hc_documents.id, 
    hc_documents.source, 
    hc_documents.section, 
    hc_documents.content,
    1 - (hc_documents.embedding <=> query_embedding) AS similarity
  FROM hc_documents
  WHERE 1 - (hc_documents.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;

-- Disable RLS for development (enable and configure policies for production)
ALTER TABLE conversations DISABLE ROW LEVEL SECURITY;
ALTER TABLE hc_documents DISABLE ROW LEVEL SECURITY;
