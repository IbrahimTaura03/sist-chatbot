# SIST Tangier AI Chatbot

AI-powered university assistant for SIST Tangier using RAG (Retrieval-Augmented Generation).

## Tech Stack
FastAPI · Groq (llama-3.3-70b) · Pinecone · NeonDB · Next.js · TypeScript · Sentence Transformers

## How to Run

### 1. Clone the repo
git clone https://github.com/IbrahimTaura03/sist-chatbot.git
cd sist-chatbot

### 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create a .env file in the backend folder with:
GROQ_API_KEY=your_groq_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=sist-chatbot
DATABASE_URL=your_neondb_url

Then run:
uvicorn main:app --reload --port 8000

### 3. Frontend setup
cd frontend
npm install

Create a .env.local file in the frontend folder with:
NEXT_PUBLIC_API_URL=http://localhost:8000

Then run:
npm run dev

### 4. Open the chatbot
Go to http://localhost:3000

## Architecture
- Frontend: Next.js (TypeScript) — chat interface with conversation history
- Backend: FastAPI (Python) — REST API, RAG pipeline, session management
- Vector DB: Pinecone — stores SIST document embeddings for semantic search
- LLM: Groq API (llama-3.3-70b-versatile) — fast open-source language model
- Database: NeonDB (PostgreSQL) — stores chat history per session
- Embeddings: sentence-transformers/all-MiniLM-L6-v2

## How RAG works
1. SIST documents are chunked and embedded into Pinecone
2. User asks a question → backend embeds it → Pinecone returns relevant chunks
3. Chunks + question sent to Groq LLM → answer generated
4. Answer saved to NeonDB and returned to frontend
