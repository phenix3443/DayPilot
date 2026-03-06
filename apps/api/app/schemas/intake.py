from pydantic import BaseModel, Field

from app.schemas.task_parse import ParseResult


class IntakeRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)


class IntakeResponse(BaseModel):
    action: str
    question: str | None = None
    task: ParseResult | None = None
