from pydantic import BaseModel, Field


class BusyEvent(BaseModel):
    start: str
    end: str


class ScheduleRequest(BaseModel):
    task: dict
    busy_events: list[BusyEvent] = Field(default_factory=list)
    work_window: tuple[str, str] = ("09:00", "18:00")


class ScheduleResponse(BaseModel):
    blocks: list[dict]
