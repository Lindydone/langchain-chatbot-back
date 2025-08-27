
def test_chat(client):
    r = client.post("/v1/chat", json={"message": "안녕"})
    assert r.status_code == 200
    assert r.json()["reply"].startswith("echo:안녕")

def test_empty_message(client):
    r = client.post("/v1/chat", json={"message": ""})
    assert r.status_code in (200, 422)
