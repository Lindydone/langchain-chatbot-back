from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from api.db.rdb import init_db, dispose_engine
from api.routers.api import api_router
from api.providers.factory import build_chat_model
from api.core.graph import create_graph

from api.db.redis import init_redis, close_redis, get_redis

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB 준비
    await init_db(create_tables=True, enable_pgvector=True)  # 테이블 생성 pgvector는 이후 rag를 위해 남겨둠

    # 모델/그래프 준비
    model = build_chat_model()
    app.state.chat_model = model
    app.state.chat_graph = create_graph(model)

    # Redis 연결 준비
    await init_redis()
    try:
        app.state.redis = get_redis()
    except RuntimeError:
        app.state.redis = None

    try:
        yield
    finally:
        await dispose_engine()
        await close_redis()

def create_app() -> FastAPI:
    app = FastAPI(title="chatbot-back", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    return app

app = create_app()
