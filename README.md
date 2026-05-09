# SIST Tangier AI Chatbot

AI-powered university assistant for SIST Tangier using RAG (Retrieval-Augmented Generation).

## Tech Stack
FastAPI · Groq (llama-3.3-70b) · Pinecone · NeonDB · Next.js · TypeScript · Sentence Transformers

## Architecture
- **Frontend**: Next.js (TypeScript) — chat interface with conversation history
- **Backend**: FastAPI (Python) — REST API, RAG pipeline, session management
- **Vector DB**: Pinecone — stores SIST document embeddings for semantic search
- **LLM**: Groq API (llama-3.3-70b-versatile) — fast open-source language model
- **Database**: NeonDB (PostgreSQL) — stores chat history per session
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2

## How it works
1. SIST documents are chunked and embedded into Pinecone
2. User asks a question → backend embeds it → Pinecone returns relevant chunks
3. Chunks + question sent to Groq LLM → answer generated
4. Answer saved to NeonDB and returned to frontend
