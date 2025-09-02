from api.core.state.chatstate import ChatState
from sqlmodel import select
from api.db.rdb import get_db
from api.db.models.chat import ChatSession

# 세션 요약 검색 노드
async def load_session_summary(state: ChatState) -> ChatState:
    session_id = state.session_id
    async with get_db() as db:
        row = (await db.exec(select(ChatSession).where(ChatSession.session_uid==session_id).limit(1))).first()  # 일부러 1건만 명시한다는 의미로 limit 추가
        state.session_summary = row.summary if row and row.summary else None
    return state