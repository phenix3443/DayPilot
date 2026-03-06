from fastapi import APIRouter

from app.schemas.schedule import ScheduleRequest, ScheduleResponse
from app.services.scheduler import schedule_task

router = APIRouter(prefix="/api", tags=["schedule"])


@router.post("/schedule", response_model=ScheduleResponse)
def schedule(payload: ScheduleRequest) -> ScheduleResponse:
    blocks = schedule_task(
        payload.task,
        [event.model_dump() for event in payload.busy_events],
        payload.work_window,
    )
    return ScheduleResponse(blocks=blocks)
