import pytest
from api.controllers.chat_controller import ChatController
from api.schemas.chat.chat import ChatRequest

@pytest.mark.asyncio
@pytest.mark.parametrize("message", ["hello", "안녕하세요", "trim?"])
async def test_chat_controller_basic(message, min_graph):
    controller = ChatController()
    req = ChatRequest(message=message, session_id="test-s1", user_id="u-1")
    res = await controller.chat(req, min_graph)

    assert hasattr(res, "reply")
    assert res.reply.startswith(f"echo:{message.strip()}")
    assert res.reply.endswith(" [persist]")