from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "DayPilot API"
