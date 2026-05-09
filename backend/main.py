import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq

load_dotenv(".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.3-70b-versatile"

groq_client = Groq(api_key=GROQ_API_KEY)

app = FastAPI(title="SIST Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load RAG gracefully ───────────────────────────────────
rag_available = False
try:
    from rag import retrieve_context
    rag_available = True
    print("✅ RAG (Pinecone) loaded successfully")
except Exception as e:
    print(f"⚠️  RAG unavailable: {e}")

# ── Load DB gracefully ────────────────────────────────────
db_available = False
try:
    from database import init_db, get_db, ChatMessage, ChatSession
    db_available = True
    print("✅ Database (NeonDB) loaded successfully")
except Exception as e:
    print(f"⚠️  Database unavailable: {e}")


class ChatRequest(BaseModel):
    question: str
    session_id: str | None = None


@app.on_event("startup")
async def startup():
    if db_available:
        try:
            await init_db()
            print("✅ NeonDB tables ready")
        except Exception as e:
            print(f"⚠️  Could not initialise DB tables: {e}")


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "llm": "groq",
        "model": GROQ_MODEL,
        "rag": "available" if rag_available else "unavailable (fix Pinecone key)",
        "database": "available" if db_available else "unavailable (fix NeonDB password)",
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    # 1. Retrieve context from Pinecone
    context = None
    if rag_available:
        try:
            context = await retrieve_context(req.question)
        except Exception as e:
            print(f"⚠️  RAG retrieval failed: {e}")

    # 2. Build messages
    if context and "No relevant context" not in context:
        system_prompt = f"""You are the official AI assistant for SIST Tangier (École Supérieure d'Ingénierie en Sciences et Technologies).

Answer clearly and professionally using ONLY the information provided below.
Do not guess or invent information. If the answer is not in the information, say so.

--- SIST Information ---
{context}
--- End of Information ---"""
    else:
        system_prompt = """You are the official AI assistant for SIST Tangier (École Supérieure d'Ingénierie en Sciences et Technologies),
a private engineering school in Tangier, Morocco.

Answer the question as helpfully as possible.
Be honest if you are not certain about specific details."""

    # 3. Call Groq
    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": req.question},
            ],
            temperature=0.2,
            max_tokens=256,
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Groq error: {str(e)}")

    # 4. Save to NeonDB
    if db_available:
        try:
            async for db in get_db():
                from sqlalchemy import select
                result = await db.execute(
                    select(ChatSession).where(ChatSession.id == session_id)
                )
                if not result.scalar_one_or_none():
                    db.add(ChatSession(id=session_id))
                    await db.flush()
                db.add(ChatMessage(session_id=session_id, role="user", content=req.question))
                db.add(ChatMessage(session_id=session_id, role="assistant", content=answer))
        except Exception as e:
            print(f"⚠️  Could not save to DB: {e}")

    return {
        "answer": answer,
        "session_id": session_id,
        "context_found": context is not None and "No relevant context" not in (context or ""),
        "rag_active": rag_available,
    }