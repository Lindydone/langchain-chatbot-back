from __future__ import annotations
from dataclasses import dataclass
from config import settings

@dataclass(frozen=True)
class PromptPolicy:
    prompt_budget: int = settings.prompt_budget
    reply_reserve: int = settings.reply_reserve
    history_ratio: float = settings.history_ratio

POLICY = PromptPolicy()
