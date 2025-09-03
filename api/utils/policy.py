from __future__ import annotations
from dataclasses import dataclass
from config import settings

@dataclass(frozen=True)
class PromptPolicy:
    prompt_budget: int = settings.prompt_budget   # 모델에 넣을 입력 토큰 최대치
    reply_reserve: int = settings.reply_reserve   # 출력 토큰 따로 빼기 
    history_ratio: float = settings.history_ratio   # 히스토리 비율

POLICY = PromptPolicy()
