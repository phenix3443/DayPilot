"""
Tests for task priority logic.
"""
from datetime import datetime, timedelta

from app.services.task_parser import parse_task_text


def test_priority_high_for_urgent_deadline():
    """测试紧急任务（1天内）优先级为 high"""
    tomorrow = datetime.now() + timedelta(days=1)
    weekday = ["一", "二", "三", "四", "五", "六", "日"][tomorrow.weekday()]
    text = f"周{weekday}完成报告"

    result = parse_task_text(text)
    assert result.priority == "high"


def test_priority_medium_for_near_deadline():
    """测试较近任务（2-3天）优先级为 medium"""
    text = "3天内完成方案"

    result = parse_task_text(text)
    assert result.priority == "medium"


def test_priority_normal_for_distant_deadline():
    """测试较远任务（>3天）优先级为 normal"""
    text = "下周五完成PPT"

    result = parse_task_text(text)
    assert result.priority == "normal"


def test_priority_normal_when_no_deadline():
    """测试无截止时间时优先级为 normal"""
    text = "做个方案"

    result = parse_task_text(text)
    assert result.priority == "normal"
