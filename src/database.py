# src/database.py
from supabase import create_client, Client
from src.config import SUPABASE_URL, SUPABASE_KEY, YOUR_TABLE_NAME
import os

# Use Render's PostgreSQL connection string if provided, else fallback to Supabase
DATABASE_URL = os.getenv("DATABASE_URL", f"postgresql://{SUPABASE_URL.split('//')[1]}")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def setup_supabase_table():
    try:
        # Enable pgvector extension
        supabase.sql("CREATE EXTENSION IF NOT EXISTS vector;")
        # Create documents table
        supabase.sql(f"""
            CREATE TABLE IF NOT EXISTS {YOUR_TABLE_NAME} (
                id BIGSERIAL PRIMARY KEY,
                content TEXT,
                metadata JSONB,
                embedding VECTOR(1024)  -- Mistral's embedding dimension
            );
        """)
        # Create function for similarity search
        supabase.sql("""
            CREATE OR REPLACE FUNCTION match_documents (
                query_embedding VECTOR(1024),
                match_count INT DEFAULT NULL,
                filter JSONB DEFAULT '{}'
            ) RETURNS TABLE (
                id BIGINT,
                content TEXT,
                metadata JSONB,
                similarity FLOAT
            ) LANGUAGE plpgsql AS $$
            BEGIN
                RETURN QUERY
                SELECT id, content, metadata, 1 - (documents.embedding <=> query_embedding) AS similarity
                FROM documents
                WHERE metadata @> filter
                ORDER BY documents.embedding <=> query_embedding
                LIMIT match_count;
            END;
            $$;
        """)
        print("Supabase table and function set up successfully.")
    except Exception as e:
        print(f"Error setting up Supabase table: {e}")
