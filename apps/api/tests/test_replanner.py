from datetime import datetime, timedelta


def test_replanner_reschedules_overdue_task():
    from app.services.replanner import reschedule_overdue_task

    # Task with deadline in past
    overdue_task = {
        "title": "过期任务",
        "duration_minutes": 120,
        "deadline": (datetime.now() - timedelta(days=1)).isoformat(),
    }

    # Reschedule to next 3 days
    new_deadline = datetime.now() + timedelta(days=3)
    result = reschedule_overdue_task(overdue_task, new_deadline)

    assert result["deadline"] == new_deadline.isoformat()
    assert result["duration_minutes"] == 120
    assert result["title"] == "过期任务"
