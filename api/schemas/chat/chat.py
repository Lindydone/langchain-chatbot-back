from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str
    stream: bool = False