from __future__ import annotations
from typing import List, Dict, Optional
import json
import logging

from api.core.state.chatstate import ChatState, Message
from api.db.redis import get_redis
from api.utils.policy import POLICY
from config import settings
from api.utils.token_count import count_messages

print("[load_history module] imported") 
logger = logging.getLogger(__name__)

logger.warning("[load_history] reached")
async def _read_all_turns_from_redis(session_id: str) -> List[Message]:
    """
    persist에서 rpush(user_msg_json, bot_msg_json) 순으로 쌓임
    LRANGE 0 -1 은 오래→최근 순. 그대로 파싱 후 Message 리스트로 평탄화.
    """
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
            msg = json.loads(item)
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                out.append({"role": str(msg["role"]), "content": str(msg["content"])})
        except Exception:
            continue

    logger.info(f"[load_history] Redis raw messages (session={session_id}): {out}")
    return out  # 오래→최근


def _split_into_turns(msgs: List[Message]) -> List[List[Message]]:
    """
    user/assistant 쌍(턴) 단위로 묶기. 짝이 안 맞으면 있는 것만 사용.
    입력: 오래→최근
    출력: [[user, assistant], [user, assistant], ...] 오래→최근 턴
    """
    turns: List[List[Message]] = []
    buf: List[Message] = []
    for m in msgs:
        if m.get("role") == "user":
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

    logger.info(f"[load_history] Split turns: {turns}")
    return turns  # 오래→최근


async def load_history(state: ChatState) -> ChatState:
    """
    1) 현재 state.messages에서 system + 최신 user의 토큰 비용 산정
    2) Redis에서 과거(turns) 로드
    3) 전체 예산에서 reply_reserve/현재메시지 비용 제외 후 history_ratio 만큼을 히스토리에 배정
    4) 최신 턴부터 예산 한도 내에서 채택 → 오래→최근으로 정렬하여 state["history"] 설정
    """
    session_id = state.get("session_id")
    if not session_id:
        state["history"] = []
        return state

    # 정책/모델(항상 토큰 기준)
    budget_total  = POLICY.prompt_budget
    reply_reserve = POLICY.reply_reserve
    history_ratio = POLICY.history_ratio
    model_name    = settings.model_name
    provider      = getattr(settings, "model_provider", None)

    logger.info(f"[load_history] Input state: {state}")

    # 현재 메시지: system 1개 + 최신 user 1개만 비용 산정
    sys_msg: Optional[Message] = next((m for m in state.get("messages", []) if m.get("role") == "system"), None)
    current_user: Optional[Message] = None
    for m in reversed(state.get("messages", [])):
        if m.get("role") == "user":
            current_user = m
            break

    current_msgs: List[Message] = []
    if sys_msg:
        current_msgs.append(sys_msg)
    if current_user:
        current_msgs.append(current_user)

    current_cost = count_messages(current_msgs, model_name=model_name, provider=provider)

    logger.info(f"[load_history] Current msgs: {current_msgs}, cost={current_cost}")

    # 히스토리 예산 계산
    available = max(budget_total - reply_reserve - current_cost, 0)
    history_budget = int(available * history_ratio) if available > 0 else 0
    if history_budget <= 0:
        state["history"] = []
        return state

    # Redis → 턴으로 묶기(오래→최근)
    all_msgs = await _read_all_turns_from_redis(session_id)
    turns = _split_into_turns(all_msgs)

    # 최신부터 예산 내에서 채택
    picked_turns: List[List[Message]] = []
    used = 0
    for turn in reversed(turns):  # 최신→오래
        c = count_messages(turn, model_name=model_name, provider=provider)
        if used + c > history_budget:
            break
        picked_turns.append(turn)
        used += c

    picked_turns.reverse()  # 과거 -> 최근 
    history: List[Message] = [m for t in picked_turns for m in t]
    state["history"] = history

    logger.info(f"[load_history] Picked history (budget={history_budget}, used={used}): {history}")
    return state
