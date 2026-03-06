import re
from datetime import datetime, timedelta

from app.schemas.task_parse import ParseResult

_DURATION_PATTERNS = [
    (re.compile(r"(\d+)\s*个?\s*小时"), 60),  # 支持 "1小时"、"1 小时"、"1个小时"、"1 个小时"
    (re.compile(r"(\d+)\s*分钟"), 1),
]

_CN_NUM = {"一": 1, "两": 2, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}

_DEFAULT_DURATION_MINUTES = 60

# 今天是星期几 (0=Mon ... 6=Sun)
_WEEKDAY_ZH = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}


def _next_weekday(target_weekday: int) -> datetime:
    today = datetime.now()
    days_ahead = (target_weekday - today.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7  # 同一天则视为下周
    return today + timedelta(days=days_ahead)


def _extract_deadline(text: str) -> datetime | None:
    # 周X / 周X前
    m = re.search(r"周([一二三四五六日天])", text)
    if m:
        return _next_weekday(_WEEKDAY_ZH[m.group(1)])
    # 今天
    if "今天" in text:
        return datetime.now()
    # 明天
    if "明天" in text:
        return datetime.now() + timedelta(days=1)
    # 后天
    if "后天" in text:
        return datetime.now() + timedelta(days=2)
    # X天后 / X天内
    m = re.search(r"(\d+)\s*天[后内]", text)
    if m:
        return datetime.now() + timedelta(days=int(m.group(1)))
    return None


def _extract_duration_minutes(text: str) -> int | None:
    # 先尝试匹配中文数字
    for cn, num in _CN_NUM.items():
        if f"{cn}个小时" in text or f"{cn}小时" in text:
            return num * 60
        if f"{cn}个半小时" in text:
            return num * 60 + 30
        if f"{cn}分钟" in text:
            return num

    # 再尝试阿拉伯数字
    for pattern, multiplier in _DURATION_PATTERNS:
        match = pattern.search(text)
        if match:
            return int(match.group(1)) * multiplier
    return None


def _extract_title(text: str) -> str:
    cleaned = re.sub(r"(周[一二三四五六日天]|今天|明天|后天|下周\w*|本周\w*)\s*(前|之前|截止)?", "", text)
    cleaned = re.sub(r"，?\s*(大概|预计|约)?\s*\d+\s*(小时|分钟).*", "", cleaned)
    cleaned = re.sub(r"(完成|做完|搞定|提交|写好)\s*", "", cleaned)
    cleaned = cleaned.strip(" ，。,.！!？?")
    return cleaned or text.strip()


def parse_task_text(text: str) -> ParseResult:
    duration = _extract_duration_minutes(text)
    deadline = _extract_deadline(text)

    missing_fields: list[str] = []
    if deadline is None:
        missing_fields.append("deadline")
    if duration is None:
        missing_fields.append("duration_minutes")

    # Auto-priority based on deadline urgency
    priority = "normal"
    if deadline is not None:
        days_until = (deadline - datetime.now()).days
        if days_until <= 1:
            priority = "high"
        elif days_until <= 3:
            priority = "medium"

    return ParseResult(
        title=_extract_title(text),
        deadline=deadline,
        duration_minutes=duration if duration is not None else _DEFAULT_DURATION_MINUTES,
        priority=priority,
        missing_fields=missing_fields,
    )
