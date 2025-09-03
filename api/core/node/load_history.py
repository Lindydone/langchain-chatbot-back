from typing import List, Optional
import json
import logging

from api.core.state.chatstate import ChatState, Message
from api.db.redis import get_redis
from api.utils.policy import POLICY
from api.utils.token_count import count_messages
from config import settings

logger = logging.getLogger(__name__)

async def _read_all_turns_from_redis(session_id: str) -> List[Message]:
    r = get_redis()
    if r is None:
        return []
    key = f"chat:{session_id}:recent"
    try:
        raw = await r.lrange(key, 0, -1)
    except Exception:
        return []
    out: List[Message] = []
    for item in raw:
        try:
            out.append(Message.model_validate_json(item)) # 이미 redis 값은 str로 제공됨
        except Exception:
            try:
                obj = json.loads(item)
                out.append(Message.model_validate(obj))
            except Exception:
                continue
    return out

def _split_into_turns(msgs: List[Message]) -> List[List[Message]]:
    """메시지를 턴으로 분리 ( 한쌍의 대화 분간 ) """
    turns: List[List[Message]] = []
    buf: List[Message] = []
    for m in msgs:
        if m.role == "user":
            if buf:
                turns.append(buf)
            buf = [m]
        else:
            if not buf:
                turns.append([m])
            else:
                buf.append(m)
                turns.append(buf)
                buf = []
    if buf:
        turns.append(buf)
    return turns

def _last_user_message(msgs: List[Message]) -> Optional[Message]:
    for m in reversed(msgs):
        if m.role == "user":
            return m
    return None

async def load_history_turn_based(state: ChatState) -> ChatState:
    session_id = state.session_id
    if not session_id:
        state.recent_candidates = []
        state.older_turns = []
        state.history = []
        state.history_budget = 0
        state.history_budget_used = 0
        state.summary_target = 0
        return state

    budget_total = POLICY.prompt_budget
    reply_reserve = POLICY.reply_reserve
    history_ratio = POLICY.history_ratio
    model_name = settings.model_name
    provider = getattr(settings, "model_provider", None)

    sys_msg: Optional[Message] = next((m for m in state.messages if m.role == "system"), None)
    current_user: Optional[Message] = _last_user_message(state.messages)

    base_msgs: List[Message] = []
    if sys_msg:
        base_msgs.append(sys_msg)
    if current_user:
        base_msgs.append(current_user)
    current_cost = count_messages(base_msgs, model_name=model_name, provider=provider) #NOTE 현재 들어온 토큰 부터 계산 후 남은 비용 분배

    available = max(budget_total - reply_reserve - current_cost, 0)
    history_budget = int(available * history_ratio) if available > 0 else 0 # 히스토리에 사용할 최대치 토큰
    if history_budget <= 0:
        state.recent_candidates = []
        state.older_turns = []
        state.history = []
        state.history_budget = 0
        state.history_budget_used = 0
        state.summary_target = 0
        return state

    all_msgs = await _read_all_turns_from_redis(session_id)
    all_turns = _split_into_turns(all_msgs)

    # TODO 나중엔 환경변수로 빼자..
    alpha = 0.12
    min_summary = 256
    max_summary = 1024
    if all_turns: #NOTE redis에 히스토리가 있으면 요약 비율 적용
        summary_target = max(min_summary, min(int(history_budget * alpha), max_summary))
    else:
        summary_target = 0

    used_recent = 0 #NOTE 현재 사용한 토큰 수 감지를 위해 사용
    recent_rev: List[List[Message]] = []
    for turn in reversed(all_turns):  # 오래 -> 최근 순이니 역순
        c = count_messages(turn, model_name=model_name, provider=provider) # 턴 토큰 수 계산
        if used_recent + c <= max(0, history_budget - summary_target): # 사용한 토큰 수 + 턴 토큰 수 가 남은 비용 이하면 다음꺼 추가
            recent_rev.append(turn)
            used_recent += c
        else:
            break

    recent_candidates = list(reversed(recent_rev)) # 다시 역순으로 돌려 모델에 넣기 좋게 오래 -> 최근으로 변경
    older_turns = all_turns[: len(all_turns) - len(recent_candidates)]  # 이번에 못들어간 턴들 
    history_flat: List[Message] = [m for t in recent_candidates for m in t]

    state.recent_candidates = recent_candidates
    state.older_turns = older_turns
    state.history = history_flat
    state.history_budget = history_budget
    state.summary_target = summary_target
    state.history_budget_used = used_recent
    return state
