from datetime import datetime

from googleapiclient.discovery import build


class GoogleCalendarAdapter:
    def __init__(self, token: str):
        self.token = token
        self.service = build("calendar", "v3", credentials=None)

    def create_event(self, calendar_id: str, event: dict) -> str:
        body = {
            "summary": event["title"],
            "start": {"dateTime": event["start"]},
            "end": {"dateTime": event["end"]},
        }
        result = self.service.events().insert(calendarId=calendar_id, body=body).execute()
        return result.get("id", "")

    def list_busy(self, calendar_id: str, start: datetime, end: datetime) -> list[dict]:
        events_result = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start.isoformat(),
                timeMax=end.isoformat(),
                singleEvents=True,
            )
            .execute()
        )
        events = events_result.get("items", [])
        return [
            {"start": e["start"]["dateTime"], "end": e["end"]["dateTime"]} for e in events
        ]
