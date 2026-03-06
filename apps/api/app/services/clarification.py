"""
Clarification state machine.

State per session_id:
  - rounds: int (number of clarification rounds done)
  - partial: dict (accumulated parsed fields across turns)

Max 2 clarification rounds, then fall back to defaults.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.schemas.task_parse import ParseResult
from app.services.task_parser_llm import parse_task_text

MAX_CLARIFY_ROUNDS = 2

_REQUIRED_FIELDS = ["deadline", "duration_minutes"]

_CLARIFY_QUESTIONS: dict[str, str] = {
    "deadline": "这件事的截止时间是什么时候？（比如‘周五前’、‘明天’）",
    "duration_minutes": "大概需要多长时间完成？（比如‘1小时’、‘30分钟’）",
}


@dataclass
class SessionState:
    rounds: int = 0
    partial: ParseResult | None = None


# In-memory store – replace with DB in production
_sessions: dict[str, SessionState] = {}


@dataclass
class IntakeResponse:
    action: str  # "ask" | "schedule"
    question: str | None = None
    task: ParseResult | None = None


def process_intake(session_id: str, text: str) -> IntakeResponse:
    state = _sessions.setdefault(session_id, SessionState())

    # Parse the new text
    parsed = parse_task_text(text)

    # Merge with any previously accumulated fields
    if state.partial is not None:
        merged = _merge(state.partial, parsed)
    else:
        merged = parsed

    state.partial = merged

    # Check which required fields are still missing
    missing = merged.missing_fields

    if not missing or state.rounds >= MAX_CLARIFY_ROUNDS:
        # Apply defaults for still-missing required fields
        if merged.deadline is None:
            merged.deadline = datetime.now() + timedelta(days=1)

        _sessions.pop(session_id, None)
        return IntakeResponse(action="schedule", task=merged)

    # Pick the highest-priority missing field to ask about
    to_ask = next((f for f in _REQUIRED_FIELDS if f in missing), missing[0])
    question = _CLARIFY_QUESTIONS.get(to_ask, f"请提供 {to_ask} 信息")

    state.rounds += 1
    return IntakeResponse(action="ask", question=question)


def _merge(base: ParseResult, update: ParseResult) -> ParseResult:
    """Merge update into base, keeping non-None values from update."""
    return ParseResult(
        title=update.title if update.title else base.title,
        deadline=update.deadline if update.deadline is not None else base.deadline,
        duration_minutes=(
            update.duration_minutes
            if "duration_minutes" not in update.missing_fields
            else base.duration_minutes
        ),
        priority=update.priority if update.priority != "normal" else base.priority,
        missing_fields=[
            f for f in _REQUIRED_FIELDS
            if _is_missing(base, update, f)
        ],
    )


def _is_missing(base: ParseResult, update: ParseResult, field: str) -> bool:
    if field == "deadline":
        return update.deadline is None and base.deadline is None
    if field == "duration_minutes":
        return (
            "duration_minutes" in update.missing_fields
            and "duration_minutes" in base.missing_fields
        )
    return False
