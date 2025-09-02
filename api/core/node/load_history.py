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
            if isinstance(item, (bytes, bytearray)):
                item = item.decode("utf-8", errors="ignore")
            obj = json.loads(item)
            if isinstance(obj, dict) and "role" in obj and "content" in obj:
                out.append(Message(role=str(obj["role"]), content=str(obj["content"])))
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
    current_cost = count_messages(base_msgs, model_name=model_name, provider=provider)

    available = max(budget_total - reply_reserve - current_cost, 0)
    history_budget = int(available * history_ratio) if available > 0 else 0
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

    alpha = 0.12
    min_summary = 256
    max_summary = 1024
    summary_target = max(min_summary, min(int(history_budget * alpha), max_summary))

    used_recent = 0
    recent_rev: List[List[Message]] = []
    for turn in reversed(all_turns):
        c = count_messages(turn, model_name=model_name, provider=provider)
        if used_recent + c <= max(0, history_budget - summary_target):
            recent_rev.append(turn)
            used_recent += c
        else:
            break

    recent_candidates = list(reversed(recent_rev))
    older_turns = all_turns[: len(all_turns) - len(recent_candidates)]
    history_flat: List[Message] = [m for t in recent_candidates for m in t]

    state.recent_candidates = recent_candidates
    state.older_turns = older_turns
    state.history = history_flat
    state.history_budget = history_budget
    state.summary_target = summary_target
    state.history_budget_used = used_recent
    return state
