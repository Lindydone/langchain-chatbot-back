
def test_chat_rest_echo(client):
    payload = {"message": "hello"}                     # ← 메시지만 전송
    r = client.post("/v1/chat", json=payload)         # (라우터 경로가 다르면 실제 경로로)
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert "hello" in body["reply"]                   # FakeModel → "echo:hello"
