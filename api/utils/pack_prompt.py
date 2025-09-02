from __future__ import annotations

from typing import List, Optional
from api.core.state.chatstate import Message
from config import settings
from api.utils.token_count import count_text, count_messages

def _measure_text(
    text: str,
    *,
    mode: str,
    model_name: str,
    provider: Optional[str],
) -> int:
    # 문자열 1개 비용 계산 기본 tokens 기준
    if not text:
        return 0
    m = (mode or "tokens").lower()
    if m == "tokens":
        return count_text(text, model_name, provider)
    return len(text)


def _measure_msgs(
    msgs: List[Message],
    *,
    mode: str,
    model_name: str,
    provider: Optional[str],
) -> int:
    """메시지 배열 비용 합계."""
    if (mode or "tokens").lower() == "tokens":  #TODO 기존엔 옵션으로 선택하는 형태로 진행, 하지만 토큰을 그냥 고정으로 사용하는 것을 선택하여 남아있는 잔재 지울 예정
        return count_messages(msgs, model_name, provider)
    return sum(
        _measure_text(m.content or "", mode=mode, model_name=model_name, provider=provider)
        for m in msgs
    )


def pack_prompt_with_ratio(
    *,
    history: List[Message],
    current_user: Message,
    system_msg: Optional[Message],
    budget_total: int,
    reply_reserve: int,
    history_ratio: float,
    mode: str = "tokens",
    model_name: Optional[str] = None,
    provider: Optional[str] = None,
) -> List[Message]:
    model_name = model_name or settings.model_name
    provider = provider or getattr(settings, "model_provider", None)

    # 입력 예산(모델 출력 예산을 제외)
    available = max(int(budget_total) - int(reply_reserve), 0)

    # ratio 보정
    try:
        history_ratio = float(history_ratio)
    except Exception:
        history_ratio = 0.7
    history_ratio = max(0.0, min(1.0, history_ratio))

    # 필수로 들어갈 현재 user 비용
    cur_cost = _measure_msgs([current_user], mode=mode, model_name=model_name, provider=provider)

    def _truncate_user_to_limit(msg: Message, limit: int) -> Message:
        """
        토큰 모드: 간이 비율로 잘라가며 limit 이하가 되게 절삭.
        chars/bytes 모드: 길이 기반 절삭.
        """
        content = msg.content or ""
        if limit <= 0:
            return Message(role="user", content="")

        if (mode or "tokens").lower() != "tokens":
            # chars/bytes는 단순 길이 컷
            if len(content) <= limit:
                return msg
            return Message(role="user", content=content[:limit])

        # tokens 모드 — 현재 비용이 이미 limit 이하라면 그대로 반환
        base_cost = _measure_text(content, mode=mode, model_name=model_name, provider=provider)
        if base_cost <= limit:
            return msg

        # 근사 비율로 컷 + 타이트닝
        approx_len = max(1, int(len(content) * (limit / max(1, base_cost))))
        cut = content[:approx_len]
        # 혹시 조금 넘으면 줄이기
        while _measure_text(cut, mode=mode, model_name=model_name, provider=provider) > limit and approx_len > 1:
            step = max(1, approx_len // 10)
            approx_len -= step
            cut = content[:approx_len]
        return Message(role="user", content=cut)

    messages: List[Message] = []

    # system 포함 판단(우선 user 보존)
    sys_included: Optional[Message] = None
    if system_msg:
        base_cost = _measure_msgs([system_msg, current_user], mode=mode, model_name=model_name, provider=provider)
        if base_cost <= available:
            sys_included = system_msg
        else:
            # system을 빼면 되는지 확인
            if cur_cost <= available:
                sys_included = None
            else:
                # user가 너무 길면 사용자 메시지 축소
                current_user = _truncate_user_to_limit(current_user, available)
                cur_cost = _measure_msgs([current_user], mode=mode, model_name=model_name, provider=provider)
                sys_included = None
    else:
        # system이 없을 때도 user 초과면 축소
        if cur_cost > available:
            current_user = _truncate_user_to_limit(current_user, available)
            cur_cost = _measure_msgs([current_user], mode=mode, model_name=model_name, provider=provider)

    # 남은 예산에서 history 배정
    sys_cost = _measure_msgs([sys_included] if sys_included else [], mode=mode, model_name=model_name, provider=provider)
    base_cost = sys_cost + cur_cost
    remaining = max(available - base_cost, 0)
    hist_budget = int(remaining * history_ratio)

    # history는 오래→최근 이므로, 최신부터 집어넣으려면 뒤에서부터
    picked: List[Message] = []
    used = 0
    for msg in reversed(history):
        c = _measure_msgs([msg], mode=mode, model_name=model_name, provider=provider)
        if used + c > hist_budget:
            break
        picked.append(msg)
        used += c
    picked.reverse()  # 다시 오래→최근으로

    # 최종 조립
    if sys_included:
        messages.append(sys_included)
    messages.extend(picked)
    messages.append(current_user)

    # 안전 클리핑: 혹시라도 초과하면 가장 오래된 history부터 제거
    total_cost = _measure_msgs(messages, mode=mode, model_name=model_name, provider=provider)
    while total_cost > available and len(messages) >= 2:
        # system 다음(또는 맨 앞)의 첫 history를 제거
        rm_idx = 1 if sys_included else 0
        # 만약 history가 없고 system만 있는 구조면 system 제거
        if rm_idx >= len(messages) - 1:
            # 마지막은 user이므로 system 제거로 초과 해소 시도
            messages.pop(0)
            sys_included = None
        else:
            messages.pop(rm_idx)
        total_cost = _measure_msgs(messages, mode=mode, model_name=model_name, provider=provider)

    return messages
