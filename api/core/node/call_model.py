from __future__ import annotations
from typing import Callable, Awaitable
from api.core.state.chatstate import ChatState, Message
from api.providers.base import BaseChatModel

def make_call_model_node(model: BaseChatModel) -> Callable[[ChatState], Awaitable[ChatState]]:  # ChatState을 받고 코루틴인 값을 반환
    async def call_model(state: ChatState) -> ChatState:
        msgs = state.messages
        if not msgs:
            state.error = "messages is empty"
            return state
        payload: list[dict] = []
        opts: dict = {}
        for m in msgs:
            payload.append({"role": m.role, "content": m.content})
        if state.opts:
            opts = state.opts.model_dump()

        try:
            reply = await model.generate(payload, **opts)
            state.messages = msgs + [Message(role="assistant", content=str(reply))]
            return state
        except Exception as e:
            state.error = f"{type(e).__name__}: {e}"
            return state

    return call_model
