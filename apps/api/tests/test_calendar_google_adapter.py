from unittest.mock import MagicMock


def test_google_adapter_maps_internal_block_to_google_event(monkeypatch):
    from app.integrations.calendar.google import GoogleCalendarAdapter

    mock_build = MagicMock()
    monkeypatch.setattr("app.integrations.calendar.google.build", mock_build)

    adapter = GoogleCalendarAdapter(token="t")
    adapter.create_event(
        "cal_1",
        {
            "title": "路演PPT",
            "start": "2026-03-08T14:00:00+08:00",
            "end": "2026-03-08T15:00:00+08:00",
        },
    )
    body = mock_build.return_value.events.return_value.insert.call_args.kwargs["body"]
    assert body["summary"] == "路演PPT"
