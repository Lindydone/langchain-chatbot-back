from __future__ import annotations
from typing import List, Dict, Any, AsyncIterator, Protocol

Message = Dict[str, str]  # {"role": "system|user|assistant", "content": "..."}

class BaseChatModel(Protocol):
    async def generate(self, messages: List[Message], **opts: Any) -> str:
        ...

    async def astream(self, messages: List[Message], **opts: Any) -> AsyncIterator[str]:
        # 기본은 스트리밍 미지원 → 한 번에 생성해서 한 조각만 흘려보냄
        yield await self.generate(messages, **opts)