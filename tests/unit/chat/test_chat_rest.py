
def test_chat_rest_echo(client):
    payload = {"message": "hello"}
    r = client.post("/v1/chat", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert "reply" in body
    assert "hello" in body["reply"]
