import os
import uuid
import httpx
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from rag import retrieve_context
from database import init_db, get_db, ChatSession, ChatMessage

load_dotenv("../.env")

OLLAMA_URL   = os.getenv("OLLAMA_BASE_URL", "http://192.168.0.143:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")

# ── App ─────────────────────────────────────────────────
app = FastAPI(title="SIST Tangier Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


# ── Schemas ──────────────────────────────────────────────
class ChatRequest(BaseModel):
    question:   str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer:       str
    context_used: str
    model:        str
    session_id:   str


class HistoryMessage(BaseModel):
    role:      str
    content:   str
    timestamp: str


class HistoryResponse(BaseModel):
    session_id: str
    messages:   list[HistoryMessage]


# ── Helper ───────────────────────────────────────────────
def build_prompt(question: str, context: str, history: list) -> str:
    history_text = ""
    for msg in history:
        label = "User" if msg.role == "user" else "Assistant"
        history_text += f"{label}: {msg.content}\n"

    return (
        f"[INST] You are a helpful admissions assistant for SIST Tangier, "
        f"a British university in Morocco. "
        f"Use ONLY the context below to answer. "
        f"If the answer is not in the context, say you don't have that information.\n\n"
        f"Context:\n{context}\n\n"
        f"Previous conversation:\n{history_text}\n"
        f"Question: {question} [/INST]"
    )


# ── Endpoints ────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db)):

    # 1. Session management
    session_id = req.session_id or str(uuid.uuid4())
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id)
    )
    if not result.scalar_one_or_none():
        db.add(ChatSession(id=session_id))
        await db.commit()

    # 2. RAG — retrieve context from Pinecone
    context = retrieve_context(req.question)

    # 3. Fetch conversation history from NeonDB (last 4 messages)
    hist_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(4)
    )
    history = list(reversed(hist_result.scalars().all()))

    # 4. Build prompt
    prompt = build_prompt(req.question, context, history)

    # 5. Call Ollama
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            res = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model":  OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 300},
                },
            )
            res.raise_for_status()
        answer = res.json()["response"].strip()
    except httpx.ConnectError:
        raise HTTPException(
            503, "Cannot connect to Ollama. Make sure Member A is running: ollama serve"
        )
    except Exception as e:
        raise HTTPException(500, f"LLM error: {str(e)}")

    # 6. Save both messages to NeonDB
    db.add(ChatMessage(session_id=session_id, role="user",      content=req.question))
    db.add(ChatMessage(session_id=session_id, role="assistant", content=answer))
    await db.commit()

    return ChatResponse(
        answer=answer,
        context_used=context[:200] + "...",
        model=OLLAMA_MODEL,
        session_id=session_id,
    )


@app.get("/history/{session_id}", response_model=HistoryResponse)
async def get_history(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
    )
    messages = result.scalars().all()
    return HistoryResponse(
        session_id=session_id,
        messages=[
            HistoryMessage(
                role=m.role,
                content=m.content,
                timestamp=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@app.get("/health")
def health():
    return {
        "status":     "ok",
        "model":      OLLAMA_MODEL,
        "ollama_url": OLLAMA_URL,
        "vector_db":  "pinecone",
        "database":   "neondb",
    }


@app.get("/")
def root():
    return {"message": "SIST Tangier Chatbot API", "docs": "/docs"} 