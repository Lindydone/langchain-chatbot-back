from fastapi import APIRouter
from api.schemas.chat.chat import ChatRequest
from api.controllers.chat_controller import ChatController

router = APIRouter()  
controller = ChatController()

@router.post("/chat")
def chat_rest(req: ChatRequest):
    return controller.echo_message(req)