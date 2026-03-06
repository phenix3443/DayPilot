from fastapi import APIRouter

from app.schemas.task_parse import ParseRequest, ParseResult
from app.services.task_parser_llm import parse_task_text

router = APIRouter(prefix="/api", tags=["parse"])


@router.post("/parse", response_model=ParseResult)
def parse_task(payload: ParseRequest) -> ParseResult:
    return parse_task_text(payload.text)
