import json
import os
from datetime import datetime

from openai import OpenAI

from app.schemas.task_parse import ParseResult


def _get_client():
    """延迟初始化 OpenAI 客户端"""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY not set in environment")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def parse_task_text(text: str) -> ParseResult:
    """使用 LLM 解析任务文本"""
    prompt = f"""从用户输入中提取任务信息，返回 JSON 格式。

用户输入：{text}

提取以下信息：
1. title: 任务标题（去除时间和时长信息）
2. deadline: 截止时间（ISO格式，如 2026-03-08T18:00:00）
   - 今天 → 今天日期
   - 明天 → 明天日期
   - 后天 → 后天日期
   - 周X → 下一个周X的日期
   - X天后/内 → 对应日期
   - 如果没有明确时间，返回 null
3. duration_minutes: 时长（分钟数）
   - 支持"1小时"、"30分钟"、"一个小时"等
   - 如果没有明确时长，返回 null

当前时间：{datetime.now().isoformat()}

只返回 JSON，不要其他内容：
{{"title": "...", "deadline": "..." or null, "duration_minutes": ... or null}}"""

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        result_text = response.choices[0].message.content.strip()
        # 移除可能的 markdown 代码块标记
        if result_text.startswith("```"):
            result_text = result_text.split("\n", 1)[1].rsplit("\n", 1)[0]

        data = json.loads(result_text)

        # 构建 ParseResult
        deadline_dt = None
        if data.get("deadline"):
            try:
                deadline_dt = datetime.fromisoformat(data["deadline"])
            except:
                pass

        duration = data.get("duration_minutes") or 60

        missing = []
        if not deadline_dt:
            missing.append("deadline")
        if not data.get("duration_minutes"):
            missing.append("duration_minutes")

        # 计算优先级
        priority = "normal"
        if deadline_dt:
            days_until = (deadline_dt - datetime.now()).days
            if days_until <= 1:
                priority = "high"
            elif days_until <= 3:
                priority = "medium"

        return ParseResult(
            title=data.get("title", text),
            deadline=deadline_dt,
            duration_minutes=duration,
            priority=priority,
            missing_fields=missing,
        )

    except Exception as e:
        # 降级：返回基本解析，并记录错误
        import sys
        print(f"LLM parsing failed: {e}", file=sys.stderr)
        return ParseResult(
            title=text,
            deadline=None,
            duration_minutes=60,
            priority="normal",
            missing_fields=["deadline", "duration_minutes"],
        )
