from typing import Dict, Any
from uuid import uuid4
from fastapi import HTTPException
from api.schemas.chat.chat import ChatRequest, ChatResponse

class ChatController:
    async def chat(self, req: ChatRequest, graph) -> ChatResponse:
        # 1) 입력 메시지 구성
        msgs = []
        if getattr(req, "system_prompt", None):
            msgs.append({"role": "system", "content": req.system_prompt})
        msgs.append({"role": "user", "content": req.message})

        # 2) LangGraph State
        state: Dict[str, Any] = {
            "messages": msgs,
            "session_id": req.session_id,
            "user_id": req.user_id,
        }
        if getattr(req, "opts", None):
            state["opts"] = req.opts

        # 3) 그래프 실행
        out = await graph.ainvoke(state)

        # 4) 에러/정상 처리
        if out.get("error"):
            raise HTTPException(status_code=500, detail=out["error"])

        reply = out["messages"][-1]["content"]
        try:
            return ChatResponse(reply=reply, session_id=state["session_id"]) 
        except TypeError:
            return ChatResponse(reply=reply)
