from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.intake import router as intake_router
from app.api.routes.parse import router as parse_router
from app.api.routes.schedule import router as schedule_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(parse_router)
app.include_router(intake_router)
app.include_router(schedule_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
