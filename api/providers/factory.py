from __future__ import annotations
from typing import Literal
from config import settings
from .base import BaseChatModel
from .openai_provider import OpenAIChatModel

Provider = Literal["openai", "remote", "local"]

def get_provider_name() -> str:
    return getattr(settings, "model_provider", "openai").lower()

def get_model_name() -> str:
    return getattr(settings, "model_name", "gpt-4o-mini")

def build_chat_model() -> BaseChatModel:
    provider = get_provider_name()

    if provider == "openai":
        key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        if not key:
            raise RuntimeError("OPENAI_API_KEY가 없습니다. (.env 설정 또는 provider=remote로 전환)")
        return OpenAIChatModel(model_name=get_model_name(), api_key=key)

    # TODO: remote/local은 추후 같은 인터페이스로 추가
    raise NotImplementedError(f"MODEL_PROVIDER='{provider}'는 아직 미구현입니다.")
