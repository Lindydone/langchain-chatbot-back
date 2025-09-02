from __future__ import annotations

from functools import lru_cache
from typing import Iterable, List, Dict, Optional

Message = Dict[str, str]

class _TokenCounter:
    name: str
    def count_text(self, text: str) -> int: ...
    def count_texts(self, texts: Iterable[str]) -> List[int]: ...


# OpenAI(tiktoken) 사용
class _OpenAITokenCounter(_TokenCounter):
    name = "openai/tiktoken"

    def __init__(self, model_name: str):
        import tiktoken  # type: ignore
        try:
            self.enc = tiktoken.encoding_for_model(model_name)
        except Exception:
            self.enc = tiktoken.get_encoding("cl100k_base")

    def count_text(self, text: str) -> int:
        return len(self.enc.encode(text or ""))

    def count_texts(self, texts: Iterable[str]) -> List[int]:
        arr = list(texts)
        try:
            batches = self.enc.encode_batch(arr)
            return [len(x) for x in batches]
        except Exception:
            return [len(self.enc.encode(t or "")) for t in arr]


# HuggingFace(transformers) 사용
#   - LLaMA/Mistral/Qwen/Gemma/bge 등
class _HFTokenCounter(_TokenCounter):
    name = "hf/transformers"

    def __init__(self, model_name: str):
        from transformers import AutoTokenizer  
        self.tok = AutoTokenizer.from_pretrained(model_name, use_fast=True)

    def count_text(self, text: str) -> int:
        return len(self.tok.encode(text or "", add_special_tokens=False))

    def count_texts(self, texts: Iterable[str]) -> List[int]:
        arr = list(texts)
        try:
            out = self.tok(
                arr, add_special_tokens=False, return_length=True, padding=False, truncation=False
            )
            lens = out["length"]
            try:
                return list(map(int, lens))
            except Exception:
                return [int(x) for x in lens]
        except Exception:
            return [len(self.tok.encode(t or "", add_special_tokens=False)) for t in arr]


# --------------------------------
# 근사치(폴백) 백엔드
# --------------------------------
class _ApproxCounter(_TokenCounter):
    name = "approx/char_div_4"

    def __init__(self, model_name: str, chars_per_token: int = 4):
        self.cpt = max(1, int(chars_per_token))

    def count_text(self, text: str) -> int:
        s = text or ""
        return max(1, len(s) // self.cpt + 1)

    def count_texts(self, texts: Iterable[str]) -> List[int]:
        return [self.count_text(t) for t in texts]


@lru_cache(maxsize=128)
def get_counter(model_name: str, provider: Optional[str] = None) -> _TokenCounter:
    p = (provider or "").lower()
    m = (model_name or "")

    # provider값 먼저 매칭 
    if p == "openai":
        try:
            return _OpenAITokenCounter(m)
        except Exception:
            return _ApproxCounter(m)

    if p in {"hf", "huggingface"}:
        try:
            return _HFTokenCounter(m)
        except Exception:
            return _ApproxCounter(m)

    # provider가 비어있거나 불명확하면 모델명 휴리스틱
    ml = m.lower()
    if ml.startswith(("gpt-", "o", "chatgpt", "text-")):
        try:
            return _OpenAITokenCounter(m)
        except Exception:
            return _ApproxCounter(m)

    if ("/" in ml) or ml.startswith(("llama", "meta-llama", "mistral", "qwen", "gemma", "phi", "bge", "intfloat/", "upskyy/")):
        try:
            return _HFTokenCounter(m)
        except Exception:
            return _ApproxCounter(m)

    return _ApproxCounter(m)


# 연결용 
def count_text(text: str, model_name: str, provider: Optional[str] = None) -> int:
    return get_counter(model_name, provider).count_text(text)

def count_texts(texts: Iterable[str], model_name: str, provider: Optional[str] = None) -> List[int]:
    return get_counter(model_name, provider).count_texts(texts)

def count_messages(
    messages: List[Message],
    model_name: str,
    provider: Optional[str] = None,
    *,
    include_roles: bool = False,
) -> int:
    contents = [m.content for m in messages]
    total = sum(count_texts(contents, model_name, provider))
    if include_roles:
        total += 2 * len(messages)
    return total
