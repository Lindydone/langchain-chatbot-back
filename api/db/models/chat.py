from typing import Optional, List
from datetime import datetime, timezone
import uuid

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Text

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id", index=True)
    session_uid: Optional[str] = Field(default=None, index=True)

    sender: str = Field(description="user or assistant")
    message: str = Field(description="message content")

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
        default_factory=now_utc,
    )

    session: Optional["ChatSession"] = Relationship(back_populates="messages")


class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_uid: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        index=True,
        unique=True,
        description="각 대화 세션을 식별하는 고유 값",
    )
    user_id: str = Field(index=True, description="사용자 고유 아이디")
    session_title: str = Field(default="New Session", description="session title")

    summary: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="세션 내용 요약 저장"
    )

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False),
        default_factory=now_utc,
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        default_factory=now_utc,
    )

    messages: List["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )