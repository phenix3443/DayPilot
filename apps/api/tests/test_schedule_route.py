"""
Tests for schedule API route.
"""
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_schedule_route_generates_blocks():
    """测试排程路由能生成日程块"""
    deadline = (datetime.now() + timedelta(days=2)).isoformat()
    response = client.post(
        "/api/schedule",
        json={
            "task": {
                "title": "测试任务",
                "duration_minutes": 120,
                "deadline": deadline,
            },
            "busy_events": [],
            "work_window": ["09:00", "18:00"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "blocks" in body
    assert len(body["blocks"]) > 0
    assert body["blocks"][0]["title"] == "测试任务"


def test_schedule_route_avoids_busy_events():
    """测试排程路由避开忙碌时段"""
    deadline = (datetime.now() + timedelta(days=1)).replace(hour=18, minute=0)
    busy_start = datetime.now().replace(hour=9, minute=0)
    busy_end = datetime.now().replace(hour=11, minute=0)

    response = client.post(
        "/api/schedule",
        json={
            "task": {
                "title": "任务",
                "duration_minutes": 60,
                "deadline": deadline.isoformat(),
            },
            "busy_events": [
                {"start": busy_start.isoformat(), "end": busy_end.isoformat()}
            ],
            "work_window": ["09:00", "18:00"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    # 验证生成的块不与忙碌时段重叠
    for block in body["blocks"]:
        block_start = datetime.fromisoformat(block["start"])
        assert block_start >= busy_end or block_start < busy_start


def test_schedule_route_returns_empty_when_impossible():
    """测试无法排程时返回空列表"""
    deadline = (datetime.now() - timedelta(days=1)).isoformat()  # 过去的截止时间
    response = client.post(
        "/api/schedule",
        json={
            "task": {
                "title": "过期任务",
                "duration_minutes": 120,
                "deadline": deadline,
            },
            "busy_events": [],
            "work_window": ["09:00", "18:00"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["blocks"] == []
