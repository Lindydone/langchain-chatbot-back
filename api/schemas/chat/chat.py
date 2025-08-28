from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="세션 ID")
    user_id: str = Field(..., min_length=1, description="사용자 ID")
    message: str = Field(..., description="사용자 입력")
    system_prompt: Optional[str] = Field(None, description="선택 시스템 지시")
    opts: Optional[Dict[str, Any]] = Field(default=None, description="모델 옵션(temperature 등)")

class ChatResponse(BaseModel):
    reply: str