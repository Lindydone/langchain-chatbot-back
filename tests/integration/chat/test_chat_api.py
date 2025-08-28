import pytest

pytestmark = [pytest.mark.integration, pytest.mark.external]

def test_chat_with_real_provider(client, req_payload):
    r = client.post("/v1/chat", json=req_payload(message="통합 테스트 핑"))
    assert r.status_code == 200
    body = r.json()
    assert body["reply"].startswith("echo:통합 테스트 핑")
    assert body["reply"].endswith(" [persist]")  # persist 노드 실행 확인

def test_chat_with_system_prompt(client, req_payload):
    payload = {
        **req_payload(message="사과는 무슨 색이니?"),
        "system_prompt": "간결하게 답해.",
        "opts": {"temperature": 0.2}
    }
    r = client.post("/v1/chat", json=payload)
    assert r.status_code == 200
    assert isinstance(r.json().get("reply"), str)
