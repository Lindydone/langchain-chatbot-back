import pytest

pytestmark = [pytest.mark.integration, pytest.mark.external]

def test_chat_with_real_provider(client):
    r = client.post("/v1/chat", json={"message": "통합 테스트 핑"})
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body.get("reply"), str)
    assert len(body["reply"]) > 0

def test_chat_with_system_prompt(client):
    payload = {
        "message": "사과는 무슨 색이니?",
        "system_prompt": "간결하게 답해.",
        "opts": {"temperature": 0.2}
    }
    r = client.post("/v1/chat", json=payload)
    assert r.status_code == 200
    assert isinstance(r.json().get("reply"), str)
