from dataclasses import dataclass
from config import settings

@dataclass(frozen=True)
class PromptPolicy:
    prompt_budget: int
    reply_reserve: int
    history_ratio: float

POLICY = PromptPolicy(
    prompt_budget=settings.prompt_budget,
    reply_reserve=settings.reply_reserve,
    history_ratio=settings.history_ratio,
)