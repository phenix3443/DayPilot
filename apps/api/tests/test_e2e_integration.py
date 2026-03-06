"""
End-to-end integration tests for DayPilot MVP.
Tests the complete flow: parse → clarify → schedule.
"""
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_complete_flow_with_full_info():
    """用户一次性提供完整信息，直接生成日程"""
    response = client.post(
        "/api/intake",
        json={"text": "周五前完成路演PPT，大概3小时", "session_id": "e2e_1"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "schedule"
    assert "路演PPT" in body["task"]["title"]  # LLM may include "完成"
    assert body["task"]["duration_minutes"] == 180


def test_complete_flow_with_clarification():
    """用户信息不足，经过1轮澄清后生成日程"""
    # Round 1: 缺少时长和截止时间
    r1 = client.post("/api/intake", json={"text": "做个方案", "session_id": "e2e_2"})
    assert r1.status_code == 200
    assert r1.json()["action"] == "ask"
    assert "截止时间" in r1.json()["question"]

    # Round 2: 提供截止时间
    r2 = client.post("/api/intake", json={"text": "明天", "session_id": "e2e_2"})
    assert r2.status_code == 200
    assert r2.json()["action"] == "ask"
    assert "多长时间" in r2.json()["question"]

    # Round 3: 达到上限，使用默认值
    r3 = client.post("/api/intake", json={"text": "不确定", "session_id": "e2e_2"})
    assert r3.status_code == 200
    body = r3.json()
    assert body["action"] == "schedule"
    assert body["task"]["duration_minutes"] == 60  # 默认值
