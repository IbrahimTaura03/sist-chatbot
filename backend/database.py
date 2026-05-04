import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, Text, DateTime, Integer
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("../.env")

# NeonDB requires asyncpg driver
DATABASE_URL = (
    os.getenv("DATABASE_URL", "")
    .replace("postgresql://", "postgresql+asyncpg://")
    .replace("?sslmode=require", "")
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"ssl": True},   # asyncpg uses this instead of sslmode
)

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


class ChatSession(Base):
    """One row per conversation session."""
    __tablename__ = "chat_sessions"

    id         = Column(String,   primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    """One row per message (user or assistant)."""
    __tablename__ = "chat_messages"

    id         = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String,  nullable=False, index=True)
    role       = Column(String,  nullable=False)   # "user" or "assistant"
    content    = Column(Text,    nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


async def init_db():
    """Create all tables in NeonDB if they don't exist yet."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ NeonDB tables ready")


async def get_db():
    """FastAPI dependency — yields a DB session per request."""
    async with AsyncSessionLocal() as session:
        yield session