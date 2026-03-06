from datetime import datetime
from typing import Protocol


class CalendarProvider(Protocol):
    def create_event(self, calendar_id: str, event: dict) -> str: ...

    def list_busy(self, calendar_id: str, start: datetime, end: datetime) -> list[dict]: ...
