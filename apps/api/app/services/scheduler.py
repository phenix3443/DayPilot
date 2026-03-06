from __future__ import annotations

from datetime import datetime, timedelta, time


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


def overlaps(block: dict, event: dict) -> bool:
    b_start = _parse_dt(block["start"])
    b_end = _parse_dt(block["end"])
    e_start = _parse_dt(event["start"])
    e_end = _parse_dt(event["end"])
    return b_start < e_end and e_start < b_end


def schedule_task(task: dict, busy_events: list[dict], work_window: tuple[str, str]) -> list[dict]:
    duration = int(task["duration_minutes"])
    deadline = _parse_dt(task["deadline"])
    title = task.get("title", "Task")

    ws_h, ws_m = map(int, work_window[0].split(":"))
    we_h, we_m = map(int, work_window[1].split(":"))

    # Start scheduling from today (or earliest busy date), day by day until deadline date
    candidate_date = min(
        [_parse_dt(e["start"]).date() for e in busy_events] + [deadline.date()]
    )

    # collect free slots
    free_slots: list[tuple[datetime, datetime]] = []
    while candidate_date <= deadline.date():
        day_start = datetime.combine(candidate_date, time(ws_h, ws_m), tzinfo=deadline.tzinfo)
        day_end = datetime.combine(candidate_date, time(we_h, we_m), tzinfo=deadline.tzinfo)
        if day_start >= deadline:
            break
        if day_end > deadline:
            day_end = deadline

        day_busy = [
            (_parse_dt(e["start"]), _parse_dt(e["end"]))
            for e in busy_events
            if _parse_dt(e["start"]).date() == candidate_date
        ]
        day_busy.sort(key=lambda x: x[0])

        cursor = day_start
        for b_start, b_end in day_busy:
            if b_start > cursor:
                free_slots.append((cursor, min(b_start, day_end)))
            if b_end > cursor:
                cursor = max(cursor, b_end)
            if cursor >= day_end:
                break
        if cursor < day_end:
            free_slots.append((cursor, day_end))

        candidate_date += timedelta(days=1)

    # allocate into 60-min blocks (last one can be shorter)
    blocks: list[dict] = []
    remaining = duration
    for slot_start, slot_end in free_slots:
        if remaining <= 0:
            break
        available = int((slot_end - slot_start).total_seconds() // 60)
        cursor = slot_start

        while available > 0 and remaining > 0:
            chunk = min(60, remaining, available)
            block_end = cursor + timedelta(minutes=chunk)
            blocks.append(
                {
                    "title": title,
                    "start": cursor.isoformat(),
                    "end": block_end.isoformat(),
                    "duration_minutes": chunk,
                }
            )
            cursor = block_end
            remaining -= chunk
            available -= chunk

    if remaining > 0:
        return []
    return blocks
