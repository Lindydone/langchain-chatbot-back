
def test_chat(client, req_payload):
    r = client.post("/v1/chat", json=req_payload(message="안녕"))
    assert r.status_code == 200
    assert r.json()["reply"].startswith("echo:안녕")

def test_empty_message(client, req_payload):
    r = client.post("/v1/chat", json=req_payload(message=""))
    assert r.status_code in (200, 422)
