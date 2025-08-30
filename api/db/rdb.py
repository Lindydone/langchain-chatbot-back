# api/db/rdb.py
from __future__ import annotations

import os
from config import settings
from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)

_ENGINE: Optional[AsyncEngine] = None
_SessionLocal: Optional[sessionmaker] = None

def build_db() -> str:
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
        _SessionLocal = sessionmaker(
            bind=_ENGINE,
            class_=AsyncSession,        
            expire_on_commit=False,
        )
    return _ENGINE


@asynccontextmanager
async def get_db() -> AsyncIterator[AsyncSession]:
    if _SessionLocal is None:
        _ensure_engine()
    assert _SessionLocal is not None
    session: AsyncSession = _SessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def init_db(*, create_tables: bool = True, enable_pgvector: bool = True) -> None:
    engine = _ensure_engine()

    from api.db.models.chat import ChatSession, ChatMessage 

    mode = (settings.db_set or "keep").lower()
    logger.info(f"DB set mode = {mode}")

    async with engine.begin() as conn:
        # 확장 생성
        if enable_pgvector:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        # reset 모드면 전체 삭제
        if mode == "recreate":
            logger.warning("Dropping ALL tables (DB_SET=recreate)")
            await conn.run_sync(SQLModel.metadata.drop_all)

        # 테이블 생성 
        if create_tables:
            logger.info("Ensuring tables (create_all)")
            await conn.run_sync(SQLModel.metadata.create_all)

async def dispose_engine() -> None:
    global _ENGINE, _SessionLocal
    if _ENGINE is not None:
        await _ENGINE.dispose()
    _ENGINE = None
    _SessionLocal = None
