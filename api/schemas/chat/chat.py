from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 입력")
    system_prompt: Optional[str] = Field(None, description="선택 시스템 지시")
    opts: Optional[Dict[str, Any]] = Field(default=None, description="모델 옵션(temperature 등)")

class ChatResponse(BaseModel):
    reply: str