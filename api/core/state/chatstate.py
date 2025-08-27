from __future__ import annotations
from typing import TypedDict, List, Dict, Optional
from pydantic import Field

Message = Dict[str, str]

class ModelOpts(TypedDict, total=False):
    temperature: float
    # 필요 시 옵션 추가 예정 (top_p, max_tokens 등)

class ChatState(TypedDict, total=False):
    messages: List[Message]

    session_id: str = Field(..., min_length=1) # 필수값으로 변경 무조건 필요한 값임 
    user_id: str = Field(..., min_length=1)
    opts: ModelOpts

    error: Optional[str]
