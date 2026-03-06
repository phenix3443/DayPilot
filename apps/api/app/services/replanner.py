from datetime import datetime


def reschedule_overdue_task(task: dict, new_deadline: datetime) -> dict:
    return {
        "title": task["title"],
        "duration_minutes": task["duration_minutes"],
        "deadline": new_deadline.isoformat(),
    }
