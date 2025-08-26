from __future__ import annotations
from typing import TypedDict, List, Dict, Optional

Message = Dict[str, str]  # {"role": "system|user|assistant", "content": "..."}

class ModelOpts(TypedDict, total=False):
    temperature: float
    # 필요 시 옵션 추가 예정 (top_p, max_tokens 등)

class ChatState(TypedDict, total=False):
    messages: List[Message]

    session_uid: Optional[str]
    user_id: Optional[str]
    opts: ModelOpts

    error: Optional[str]
