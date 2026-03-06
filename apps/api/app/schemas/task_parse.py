from datetime import datetime

from pydantic import BaseModel, Field


class ParseRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ParseResult(BaseModel):
    title: str
    deadline: datetime | None = None
    duration_minutes: int | None = None
    priority: str = "normal"
    missing_fields: list[str] = Field(default_factory=list)
