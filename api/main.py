from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.db.rdb import init_db, dispose_engine
from api.routers.api import api_router  

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시: SQLModel 테이블 생성
    await init_db(create_tables=True, enable_pgvector=True)
    yield
    # 앱 종료 시: DB 엔진 정리
    await dispose_engine()

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
