# api/core/graph.py
from __future__ import annotations
from langgraph.graph import StateGraph, START, END

from api.core.state.chatstate import ChatState
from api.providers.base import BaseChatModel

# 멀티턴 노드들
from api.core.node.load_summary import load_session_summary
from api.core.node.load_history import load_history_turn_based
from api.core.node.build_prompt import build_prompt
from api.core.node.call_model import make_call_model_node
from api.core.node.persist import persist

# 간단한 후처리(없으면 패스)( 이후 수정 및 추가 예정)
async def postprocess(state: ChatState) -> ChatState:
    # 이미 에러가 있으면 그대로 통과
    if state.error:
        return state
    return state

def create_graph(model: BaseChatModel):
    b = StateGraph(ChatState)

    # 1. 과거 요약 로드(DB)
    b.add_node("load_session_summary", load_session_summary)
    # 2. 과거 대화 로드(REDIS, 예산 기반)
    b.add_node("load_history", load_history_turn_based)
    # 3. 프롬프트 구성(요약+히스토리+현재 user 메시지 → budget pack)
    b.add_node("build_prompt", build_prompt)
    # 4. 모델 호출
    b.add_node("call_model", make_call_model_node(model))
    # 5. 후처리(미구현)
    b.add_node("postprocess", postprocess)
    # 6. 저장 
    b.add_node("persist", persist)


    # 엣지 연결
    b.add_edge(START, "load_session_summary")
    b.add_edge("load_session_summary", "load_history")
    b.add_edge("load_history", "build_prompt")
    b.add_edge("build_prompt", "call_model")
    b.add_edge("call_model", "postprocess")
    b.add_edge("postprocess", "persist")
    b.add_edge("persist", END)

    return b.compile()
