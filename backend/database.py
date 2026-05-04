import os
=======
import ssl
>>>>>>> 91f3e15 (save changes before pull)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Text, DateTime, Integer
from datetime import datetime
from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv("../.env")

# NeonDB requires asyncpg driver
DATABASE_URL = (
    os.getenv("DATABASE_URL", "")
    .replace("postgresql://", "postgresql+asyncpg://")
    .replace("?sslmode=require", "")
)
=======
load_dotenv(".env")

DATABASE_URL = os.getenv("DATABASE_URL", "")

# ── Fix 1: Convert scheme for asyncpg ───────────────────
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# ── Fix 2: Strip ?sslmode=require — asyncpg rejects it ──
# SSL is handled via connect_args below instead
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]

# ── Fix 3: Proper SSL context for NeonDB ─────────────────
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = True
ssl_context.verify_mode = ssl.CERT_REQUIRED
>>>>>>> 91f3e15 (save changes before pull)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
<<<<<<< HEAD
    connect_args={"ssl": True},   # asyncpg uses this instead of sslmode
)

engine = create_async_engine(DATABASE_URL, echo=False)

=======
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True,       # reconnect if DB drops connection
    pool_size=5,
    max_overflow=10,
)

>>>>>>> 91f3e15 (save changes before pull)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class ChatSession(Base):
<<<<<<< HEAD
    """One row per conversation session."""
    __tablename__ = "chat_sessions"

    id         = Column(String,   primary_key=True)
=======
    __tablename__ = "chat_sessions"

    id = Column(String, primary_key=True)
>>>>>>> 91f3e15 (save changes before pull)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
<<<<<<< HEAD
    """One row per message (user or assistant)."""
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String,  nullable=False, index=True)
    role       = Column(String,  nullable=False)   # "user" or "assistant"
    content    = Column(Text,    nullable=False)
=======
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
>>>>>>> 91f3e15 (save changes before pull)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
<<<<<<< HEAD
    """Create all tables in NeonDB if they don't exist yet."""
=======
>>>>>>> 91f3e15 (save changes before pull)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ NeonDB tables ready")


<<<<<<< HEAD
async def get_db():
    """FastAPI dependency — yields a DB session per request."""
    async with AsyncSessionLocal() as session:
        yield session
=======
# ── Fix 4: Correct async generator pattern for FastAPI Depends ──
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
>>>>>>> 91f3e15 (save changes before pull)
