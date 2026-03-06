from fastapi import FastAPI

from app.api.routes.parse import router as parse_router

app = FastAPI()
app.include_router(parse_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
