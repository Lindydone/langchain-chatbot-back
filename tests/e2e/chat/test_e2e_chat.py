import pytest
pytestmark = [pytest.mark.e2e]

def test_e2e_chat_basic(http, req_payload):
    r = http.post("/v1/chat", json=req_payload(message="E2E 핑"))
    assert r.status_code == 200
    assert "reply" in r.json()