"""
Comprehensive test suite for natural language parsing.
Tests various input patterns to ensure robust parsing.
"""
import pytest
from app.services.task_parser import parse_task_text


class TestDurationParsing:
    """测试时长解析的各种格式"""

    @pytest.mark.parametrize("text,expected_minutes", [
        # 阿拉伯数字
        ("1小时", 60),
        ("2小时", 120),
        ("30分钟", 30),
        # 带空格
        ("1 小时", 60),
        ("2 小时", 120),
        # 带"个"字
        ("1个小时", 60),
        ("2个小时", 120),
        ("1 个小时", 60),
        # 中文数字
        ("一小时", 60),
        ("两小时", 120),
        ("一个小时", 60),
        ("两个小时", 120),
        ("三小时", 180),
    ])
    def test_duration_formats(self, text, expected_minutes):
        result = parse_task_text(f"完成任务，{text}")
        assert result.duration_minutes == expected_minutes


class TestDeadlineParsing:
    """测试截止时间解析"""

    def test_today(self):
        result = parse_task_text("今天完成报告")
        assert result.deadline is not None
        assert "deadline" not in result.missing_fields

    def test_tomorrow(self):
        result = parse_task_text("明天完成报告")
        assert result.deadline is not None

    def test_day_after_tomorrow(self):
        result = parse_task_text("后天完成报告")
        assert result.deadline is not None

    def test_weekday(self):
        result = parse_task_text("周五完成报告")
        assert result.deadline is not None

    def test_days_later(self):
        result = parse_task_text("3天后完成报告")
        assert result.deadline is not None


class TestCompleteInputs:
    """测试完整输入（包含标题、时长、截止时间）"""

    @pytest.mark.parametrize("text", [
        "周五前完成路演PPT，大概3小时",
        "明天花2小时做方案",
        "今天晚上一个小时完成报告",
        "后天用1 个小时写文档",
    ])
    def test_complete_inputs(self, text):
        result = parse_task_text(text)
        assert result.title
        assert result.duration_minutes > 0
        assert result.deadline is not None
        assert len(result.missing_fields) == 0


class TestIncompleteInputs:
    """测试不完整输入"""

    def test_only_title(self):
        result = parse_task_text("做方案")
        assert result.title == "做方案"
        assert "deadline" in result.missing_fields
        assert "duration_minutes" in result.missing_fields

    def test_missing_duration(self):
        result = parse_task_text("明天完成报告")
        assert result.deadline is not None
        assert "duration_minutes" in result.missing_fields

    def test_missing_deadline(self):
        result = parse_task_text("花2小时做PPT")
        assert result.duration_minutes == 120
        assert "deadline" in result.missing_fields
