from __future__ import annotations
from typing import Dict, Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(..., description="메시지 형식 = (user, system)")
    content: str = Field(..., description="메시지 내용")


class ModelOpts(BaseModel):
    temperature: Optional[float] = Field(
        None, ge=0, le=2,
        description="온도 (0~2 사이)"
    )
    # 필요 시 top_p, max_tokens 등 추가 가능

class ChatState(BaseModel):
    # 공통 사용
    session_id: str = Field(..., min_length=1, description="세션 식별자")
    user_id: str = Field(..., min_length=1, description="사용자 식별자")

    messages: List[Message] = Field(default_factory=list, description="대화 메시지 리스트")
    opts: Optional[ModelOpts] = Field(None, description="모델 옵션")
    error: Optional[str] = Field(None, description="에러 메시지")

    #내부 사용
    session_summary: Optional[str] = Field(None, description="세션 요약")

    # 히스토리 관련 선언
    recent_candidates: List[List[Message]] = Field(default_factory=list, description="예산 내 최신 턴 후보들")
    older_turns: List[List[Message]] = Field(default_factory=list, description="과거 턴")
    history: List[Message] = Field(default_factory=list,description="과거 대화")
    history_budget: Optional[int] = Field(0, description="과거 대화 예산")
    history_budget_used: Optional[int] = Field(0, description="과거 대화 예산 사용량")
    summary_target: Optional[int] = Field(0, description="요약 대상")

    # 프롬프트 예산 전략 선언
    prompt_budget: Optional[int] = None
    reply_reserve: Optional[int] = None
    history_ratio: Optional[float] = None