from __future__ import annotations
from typing import Optional

from api.core.state.chatstate import ChatState, Message
from api.utils.pack_prompt import pack_prompt_with_ratio
from api.utils.policy import POLICY
from config import settings

def _last_user_message(msgs: list[Message]) -> Optional[Message]:
    """지금 사용자가 한 질문 파악"""
    for m in reversed(msgs):
        if m.role == "user":
            return m
    return None

def build_prompt(state: ChatState) -> ChatState:
    # 입력 메시지에서 system / 최신 user 분리
    msgs: list[Message] = state.messages
    system_msg: Optional[Message] = next((m for m in msgs if m.role == "system"), None)
    current_user: Optional[Message] = _last_user_message(msgs)

    if current_user is None:
        state.error = (state.error or "") + " [build_prompt:missing user msg]"
        return state

    # 과거 대화/요약
    history: list[Message] = state.history
    summary: Optional[str] = state.session_summary
    summary_msg: Optional[Message] = (
        Message(role="system", content=f"[Session summary]\n{summary}") if summary else None
    )

    # system + summary 병합 (system은 하나만 유지)
    merged_system: Optional[Message] = system_msg
    if summary_msg:
        merged_system = Message(
            role="system",
            content=f"{summary_msg.content}\n\n{system_msg.content}",
        )
    elif system_msg:
        merged_system = system_msg
    elif summary_msg:
        merged_system = summary_msg

    # 프롬프트 예산/전략 (state가 우선, 없으면 POLICY 설정으로 진행)( 앞의 노드 붙을거 고려 )
    budget_total  = getattr(state, "prompt_budget",  None) or POLICY.prompt_budget
    reply_reserve = getattr(state, "reply_reserve",  None) or POLICY.reply_reserve
    history_ratio = getattr(state, "history_ratio",  None) or POLICY.history_ratio
    model_name = settings.model_name

    # 패킹 실행 (system 1개 + user 1개 형태로 맞추는 유틸)
    packed: list[Message] = pack_prompt_with_ratio(
        history=history,
        current_user=current_user,
        system_msg=merged_system,
        budget_total=budget_total,
        reply_reserve=reply_reserve,
        history_ratio=history_ratio,
        model_name=model_name,
    )

    # 결과를 state에 반영
    state.messages = packed
    return state
