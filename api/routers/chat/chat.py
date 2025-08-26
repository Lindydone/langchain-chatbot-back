from fastapi import APIRouter, Request
from api.schemas.chat.chat import ChatRequest, ChatResponse
from api.controllers.chat_controller import ChatController

router = APIRouter()  
controller = ChatController()

@router.post("/chat", response_model=ChatResponse)
async def chat_rest(req: ChatRequest, request: Request):
    graph = request.app.state.chat_graph
    return await controller.chat(req, graph)