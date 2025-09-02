from typing import Dict, Any, List
from uuid import uuid4
from fastapi import HTTPException
from api.schemas.chat.chat import ChatRequest, ChatResponse
from api.core.state.chatstate import ChatState, Message, ModelOpts

class ChatController:
    async def chat(self, req: ChatRequest, graph) -> ChatResponse:
        # 1) 입력 메시지 구성
        msgs: List[Message] = []
        system_prompt = getattr(req, "system_prompt", None)
        if system_prompt:
            msgs.append(Message(role="system", content=system_prompt))
        msgs.append(Message(role="user", content=req.message))

        # 2) LangGraph State
        init_state = ChatState(
            session_id=req.session_id,
            user_id=req.user_id,
            messages=msgs,
            opts=ModelOpts(**req.opts) if getattr(req, "opts", None) else None,
        )

        # 3) 그래프 실행
        out_raw = await graph.ainvoke(init_state)

        # dict -> ChatState 강제 변환 TODO 이후 수정 예정
        if isinstance(out_raw, dict):
            try:
                out = ChatState.model_validate(out_raw)   # messages의 dict들도 자동으로 Message로 파싱됨
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to coerce graph output: {e}")
        else:
            out = out_raw
            
        # 4) 에러/정상 처리
        if out.error:
            raise HTTPException(status_code=500, detail=out.error)

        last = out.messages[-1] # 마지막 내용인 assistant 메시지 추출
        reply = last.content if isinstance(last, Message) else str(last) # 마지막 내용인 assistant 메시지 추출
        
        return ChatResponse(reply=reply, session_id=out.session_id)
