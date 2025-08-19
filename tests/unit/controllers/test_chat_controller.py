import pytest
from api.controllers.chat_controller import ChatController
from api.schemas.chat.chat import ChatRequest


@pytest.fixture(scope="module")
def controller():
    return ChatController()


@pytest.mark.parametrize(
    "session_id,message,stream",
    [
        ("s1", "hello", False),
        ("user-42", "안녕하세요", True),
        ("abc", "   trim?   ", False),
    ],
)
def test_echo_message_basic(controller, session_id, message, stream):
    req = ChatRequest(session_id=session_id, message=message, stream=stream)
    res = controller.echo_message(req)

    assert isinstance(res, dict)
    assert res["session_id"] == session_id
    assert res["reply"] == message
