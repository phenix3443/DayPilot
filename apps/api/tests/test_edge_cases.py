"""
Edge case tests for DayPilot MVP.
"""
from datetime import datetime, timedelta

from fastapi.testclient import TestClient

from app.main import app
from app.services.task_parser import parse_task_text

client = TestClient(app)


def test_parse_handles_very_long_text():
    """测试处理超长文本"""
    long_text = "完成报告" + "非常重要" * 100
    result = parse_task_text(long_text)
    assert result.title is not None
    assert len(result.title) > 0


def test_parse_handles_special_characters():
    """测试处理特殊字符"""
    text = "完成@#$%报告，明天！！！"
    result = parse_task_text(text)
    assert "报告" in result.title


def test_intake_handles_empty_session():
    """测试空会话ID被正确拒绝"""
    response = client.post("/api/intake", json={"text": "做方案", "session_id": ""})
    assert response.status_code == 422  # 应该拒绝空会话ID


def test_schedule_handles_zero_duration():
    """测试零时长任务"""
    deadline = (datetime.now() + timedelta(days=1)).isoformat()
    response = client.post(
        "/api/schedule",
        json={
            "task": {"title": "任务", "duration_minutes": 0, "deadline": deadline},
            "busy_events": [],
            "work_window": ["09:00", "18:00"],
        },
    )
    # 应该返回422错误（Pydantic验证失败）
    assert response.status_code == 422
