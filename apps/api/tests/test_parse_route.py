import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.parametrize("text,expected_title,expected_duration,missing", [
    ("周五前完成路演PPT，大概3小时", "路演PPT", 180, []),
    ("做方案", "做方案", 60, ["deadline", "duration_minutes"]),  # 无截止时间和时长 -> 两者都缺失
    ("明天完成报告", "报告", 60, ["duration_minutes"]),  # 无时长 -> missing duration
])
def test_parse_route_extracts_fields(text, expected_title, expected_duration, missing):
    r = client.post("/api/parse", json={"text": text})
    assert r.status_code == 200
    data = r.json()
    assert data["duration_minutes"] == expected_duration
    assert set(data["missing_fields"]) == set(missing)


def test_parse_route_returns_422_on_empty_text():
    r = client.post("/api/parse", json={"text": ""})
    assert r.status_code == 422
