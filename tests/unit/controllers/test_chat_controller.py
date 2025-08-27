# tests/unit/controllers/test_chat_controller.py
import pytest
from api.controllers.chat_controller import ChatController
from api.schemas.chat.chat import ChatRequest
from api.core.graph import create_graph

class FakeModel:
    async def generate(self, messages, **opts):
        last = next((m["content"] for m in reversed(messages) if m["role"]=="user"), "")
        return f"echo:{last.strip()}"

@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["hello", "안녕하세요", "   trim?   "])
async def test_chat_controller_basic(message):
    controller = ChatController()
    graph = create_graph(FakeModel())       # 컨트롤러 단위로도 Fake 그래프 사용
    req = ChatRequest(message=message)
    res = await controller.chat(req, graph)
    assert hasattr(res, "reply")
    assert "echo" in res.reply
