from __future__ import annotations
from typing import List, Dict, AsyncIterator, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .base import BaseChatModel, Message

def _to_lc_messages(msgs: List[Message]):
    out = []
    for m in msgs:
        role, content = m.get("role"), m.get("content", "")
        if role == "system":
            out.append(SystemMessage(content))
        elif role == "assistant":
            out.append(AIMessage(content))
        else:
            out.append(HumanMessage(content))
    return out

class OpenAIChatModel(BaseChatModel):
    def __init__(
        self,
        model_name: str,
        api_key: str,
        temperature: float = 0.2,
        timeout: float | None = 60.0,
        max_retries: int = 2,
    ):
        # LangChain OpenAI LLM
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
            streaming=True,  # 스트리밍 지원
        )

    async def generate(self, messages: List[Message], **opts: Any) -> str:
        resp = await self.llm.ainvoke(_to_lc_messages(messages))
        return resp.content or ""

    async def astream(self, messages: List[Message], **opts: Any) -> AsyncIterator[str]:
        async for chunk in self.llm.astream(_to_lc_messages(messages)):
            if chunk and chunk.content:
                yield chunk.content
