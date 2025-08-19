from fastapi import APIRouter

from api.routers import health
from api.routers.chat import chat

api_router = APIRouter()

# Health check router
api_router.include_router(health.router, prefix="")

# # Chat routers
api_router.include_router(chat.router, prefix="/v1") 
