def test_chat_rest_echo(client):
    payload = {"session_id": "s1", "message": "hello", "stream": False}
    r = client.post("/v1/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["session_id"] == "s1"
    assert "reply" in body
    assert "hello" in body["reply"]