from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_intake_stops_after_two_clarifications():
    # 第一次：信息不足 -> ask
    r1 = client.post("/api/intake", json={"text": "做个方案", "session_id": "s1"})
    assert r1.status_code == 200
    assert r1.json()["action"] == "ask"

    # 第二次：还是不足 -> ask
    r2 = client.post("/api/intake", json={"text": "尽快", "session_id": "s1"})
    assert r2.status_code == 200
    assert r2.json()["action"] == "ask"

    # 第三次：达到上限 -> schedule（默认值补齐）
    r3 = client.post("/api/intake", json={"text": "不知道多久", "session_id": "s1"})
    assert r3.status_code == 200
    body = r3.json()
    assert body["action"] == "schedule"
    assert body["task"]["duration_minutes"] == 60
    assert "deadline" in body["task"]["missing_fields"]
