from fastapi import APIRouter

from app.schemas.intake import IntakeRequest, IntakeResponse
from app.services.clarification import process_intake

router = APIRouter(prefix="/api", tags=["intake"])


@router.post("/intake", response_model=IntakeResponse)
def intake(payload: IntakeRequest) -> IntakeResponse:
    result = process_intake(payload.session_id, payload.text)
    return IntakeResponse(
        action=result.action,
        question=result.question,
        task=result.task,
    )
