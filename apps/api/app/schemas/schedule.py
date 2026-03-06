from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BusyEvent(BaseModel):
    start: str
    end: str


class TaskInput(BaseModel):
    title: str
    duration_minutes: int = Field(..., gt=0)
    deadline: str

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except ValueError as e:
            raise ValueError(f"Invalid ISO datetime format: {e}")
        return v


class ScheduleBlock(BaseModel):
    title: str
    start: str
    end: str
    duration_minutes: int


class ScheduleRequest(BaseModel):
    task: TaskInput
    busy_events: list[BusyEvent] = Field(default_factory=list)
    work_window: tuple[str, str] = ("09:00", "18:00")


class ScheduleResponse(BaseModel):
    blocks: list[ScheduleBlock]
