from __future__ import annotations
from typing import Callable
from api.core.state.chatstate import ChatState, Message
from api.providers.base import BaseChatModel

def make_call_model_node(model: BaseChatModel) -> Callable[[ChatState], "ChatState"]:
    async def call_model(state: ChatState) -> ChatState:
        msgs = state.get("messages", [])
        if not msgs:
            return {"error": "messages is empty"}
        try:
            reply = await model.generate(msgs, **state.get("opts", {}))
            new_messages: list[Message] = msgs + [{"role": "assistant", "content": reply}]
            return {"messages": new_messages}
        except Exception as e:
            # 실패 시 에러만 채워서 종료(라우터에서 처리)
            return {"error": f"{type(e).__name__}: {e}"}

    return call_model
