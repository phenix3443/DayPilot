from datetime import datetime

from app.services.scheduler import overlaps, schedule_task


def test_scheduler_avoids_existing_events_and_splits_blocks():
    task = {
        "title": "路演PPT",
        "duration_minutes": 180,
        "deadline": "2026-03-10T18:00:00+08:00",
    }
    busy = [
        {"start": "2026-03-08T09:00:00+08:00", "end": "2026-03-08T11:00:00+08:00"},
        {"start": "2026-03-08T14:00:00+08:00", "end": "2026-03-08T15:00:00+08:00"},
    ]

    blocks = schedule_task(task, busy, work_window=("09:00", "18:00"))

    assert sum(b["duration_minutes"] for b in blocks) == 180
    for b in blocks:
        for event in busy:
            assert not overlaps(b, event)


def test_scheduler_returns_empty_if_no_time_before_deadline():
    task = {
        "title": "紧急任务",
        "duration_minutes": 120,
        "deadline": "2026-03-08T09:30:00+08:00",
    }
    busy = [{"start": "2026-03-08T09:00:00+08:00", "end": "2026-03-08T18:00:00+08:00"}]

    blocks = schedule_task(task, busy, work_window=("09:00", "18:00"))
    assert blocks == []
