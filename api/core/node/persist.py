from __future__ import annotations
from typing import Any
import json
from api.core.state.chatstate import ChatState
from config import settings
from api.core.state.chatstate import Message
from api.db.models.chat import ChatSession, ChatMessage 
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.db.rdb import get_db 
from api.db.redis import get_redis 

async def _ensure_session(session: AsyncSession, session_id: str, user_id: str) -> ChatSession:
    stmt = select(ChatSession).where(ChatSession.session_uid == session_id).limit(1)
    result = await session.exec(stmt)

    row = result.first()

    if row:
        return row

    row = ChatSession(session_uid=session_id, user_id=user_id, session_title="New Session")
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def _write_pg(session_id: str, user_id: str, user_msg: str, bot_msg: str):
    async with get_db() as db:
        sess = await _ensure_session(db, session_id, user_id)
        db.add(ChatMessage(session_id=sess.id, session_uid=session_id, sender="user", message=user_msg))
        db.add(ChatMessage(session_id=sess.id, session_uid=session_id, sender="assistant", message=bot_msg))
        await db.commit()

async def _write_redis(session_id: str, user_msg: Message, bot_msg: Message):
    r = get_redis()    
    key = f"chat:{session_id}:recent"
    # 리스트에 최근 20개만 유지 
    await r.rpush(key, user_msg.model_dump_json(), bot_msg.model_dump_json())
    await r.ltrim(key, -40, -1)  # user/bot 한 쌍 기준 20쌍  40개

async def persist(state: ChatState) -> ChatState:
    msgs = state.messages
    if len(msgs) == 0:
        return state
    user_m = msgs[-2] if len(msgs) >= 2 else Message(role="user", content="")
    bot_m  = msgs[-1] # 마지막은 어시스턴트

    try:
        # 1) Postgres
        await _write_pg(
            session_id=state.session_id or "default",
            user_id=state.user_id or "anon",
            user_msg=user_m.content,
            bot_msg=bot_m.content,
        )
    except Exception as e:
        # 저장 실패는 상태에만
        state.error = (state.error or "") + f" [pg:{type(e).__name__}:{e}]"

    try:
        # 2) Redis
        await _write_redis(
            session_id=state.session_id or "default",
            user_msg=user_m,
            bot_msg=bot_m,
        )
    except Exception as e:
        state.error = (state.error or "") + f" [redis:{type(e).__name__}:{e}]"

    return state