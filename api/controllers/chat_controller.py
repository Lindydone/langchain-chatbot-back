from typing import Dict, Any
from fastapi import HTTPException
from api.schemas.chat.chat import ChatRequest, ChatResponse

class ChatController:
    async def chat(self, req: ChatRequest, graph) -> ChatResponse:
        # 1) LangGraph 상태 만들기
        msgs = []
        if req.system_prompt:
            msgs.append({"role":"system", "content": req.system_prompt})
        msgs.append({"role":"user", "content": req.message})

        state: Dict[str, Any] = {"messages": msgs}
        if req.opts:  # temperature 등 전달
            state["opts"] = req.opts

        # 2) 그래프 실행
        out = await graph.ainvoke(state)

        # 3) 에러/정상 처리
        if out.get("error"):
            raise HTTPException(status_code=500, detail=out["error"])

        reply = out["messages"][-1]["content"]
        return ChatResponse(reply=reply)
