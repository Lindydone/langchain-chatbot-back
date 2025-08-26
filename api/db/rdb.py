from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

_ENGINE: Optional[AsyncEngine] = None
_SessionLocal: Optional[sessionmaker] = None


def build_db() -> str:
    """
    URL 우선순위:
      1) DATABASE_URL(또는 POSTGRES_URL) 전체 DSN
      2) 개별 항목으로 조립(POSTGRES_*)
    """
    env_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if env_url:
        return env_url

    scheme = os.getenv("POSTGRES_SCHEME", "postgresql+asyncpg")
    host   = os.getenv("POSTGRES_HOST", "postgres")
    port   = os.getenv("POSTGRES_PORT", "5432")
    db     = os.getenv("POSTGRES_DATABASE", "chatbot")
    user   = os.getenv("POSTGRES_USER", "chatbot")
    pwd    = os.getenv("POSTGRES_PASSWORD", "chatbot")
    return f"{scheme}://{user}:{pwd}@{host}:{port}/{db}"


def _ensure_engine() -> AsyncEngine:
    global _ENGINE, _SessionLocal
    if _ENGINE is None:
        _ENGINE = create_async_engine(
            build_db(),
            echo=os.getenv("DB_ECHO", "False").lower() == "true",
            future=True,
            pool_pre_ping=True,
        )
        _SessionLocal = sessionmaker(bind=_ENGINE, class_=AsyncSession, expire_on_commit=False)
    return _ENGINE


@asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    """FastAPI Depends에서 사용하는 세션 제공자."""
    if _SessionLocal is None:
        _ensure_engine()
    assert _SessionLocal is not None
    session: AsyncSession = _SessionLocal()  # type: ignore
    try:
        yield session
    finally:
        await session.close()


async def init_db(*, create_tables: bool = True, enable_pgvector: bool = True) -> None:
    """
    앱 시작 시 호출:
      - (옵션) pgvector 확장 설치
      - (옵션) SQLModel 기반 테이블 생성
    Alembic을 쓸 땐 create_tables=False 권장.
    """
    engine = _ensure_engine()

    from api.db.models.chat import ChatSession, ChatMessage

    async with engine.begin() as conn:
        if enable_pgvector:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        if create_tables:
            await conn.run_sync(SQLModel.metadata.create_all)


async def dispose_engine() -> None:
    global _ENGINE, _SessionLocal
    if _ENGINE is not None:
        await _ENGINE.dispose()
    _ENGINE = None
    _SessionLocal = None
