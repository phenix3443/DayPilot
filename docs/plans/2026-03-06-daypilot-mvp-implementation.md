# DayPilot MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a production-usable MVP where users enter natural-language tasks, system asks at most 2 clarification rounds, auto-schedules tasks, and syncs to Google Calendar.

**Architecture:** Use a monorepo with `apps/api` (FastAPI) and `apps/web` (Next.js). Keep AI parsing and scheduling in backend domain services with strict Pydantic schemas and deterministic scheduling rules. Use PostgreSQL as source of truth, Redis+Celery for async replan/sync jobs, and a provider adapter for calendar integration.

**Tech Stack:** Python 3.11, FastAPI, Pydantic v2, SQLAlchemy, Alembic, PostgreSQL, Redis, Celery, pytest, Next.js, TypeScript, React Query, Playwright.

---

## Implementation Rules (must follow)

- Apply @superpowers:test-driven-development for every task.
- Before claiming completion, apply @superpowers:verification-before-completion.
- Keep commits small; one logical task per commit.
- DRY + YAGNI: only implement MVP scope from `docs/plans/2026-03-06-daypilot-design.md`.

---

### Task 1: Repository scaffolding and tooling baseline

**Files:**
- Create: `apps/api/app/main.py`
- Create: `apps/api/app/config.py`
- Create: `apps/api/tests/test_health.py`
- Create: `apps/web/package.json`
- Create: `apps/web/next.config.ts`
- Create: `apps/web/app/page.tsx`
- Modify: `pyproject.toml`

**Step 1: Write the failing test**

```python
# apps/api/tests/test_health.py
from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint_returns_ok():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_health.py -v`
Expected: FAIL with import/module error (app not created yet).

**Step 3: Write minimal implementation**

```python
# apps/api/app/main.py
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_health.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add pyproject.toml apps/api apps/web
git commit -m "chore: scaffold api and web baseline"
```

---

### Task 2: Database models and migration foundation

**Files:**
- Create: `apps/api/app/db/base.py`
- Create: `apps/api/app/db/models.py`
- Create: `apps/api/alembic.ini`
- Create: `apps/api/alembic/env.py`
- Create: `apps/api/alembic/versions/0001_initial.py`
- Test: `apps/api/tests/test_models.py`

**Step 1: Write the failing test**

```python
# apps/api/tests/test_models.py
from app.db.models import Task


def test_task_model_has_required_fields():
    cols = {c.name for c in Task.__table__.columns}
    assert {"id", "user_id", "title", "deadline", "duration_minutes", "status"}.issubset(cols)
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_models.py -v`
Expected: FAIL with model import error.

**Step 3: Write minimal implementation**

```python
# apps/api/app/db/models.py
class Task(Base):
    __tablename__ = "tasks"
    id = mapped_column(UUID, primary_key=True)
    user_id = mapped_column(UUID, nullable=False, index=True)
    title = mapped_column(String(255), nullable=False)
    deadline = mapped_column(DateTime(timezone=True), nullable=True)
    duration_minutes = mapped_column(Integer, nullable=False, default=60)
    status = mapped_column(String(32), nullable=False, default="pending")
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_models.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/db apps/api/alembic apps/api/tests/test_models.py
git commit -m "feat: add initial postgres models and migration setup"
```

---

### Task 3: Task parser API with strict schema

**Files:**
- Create: `apps/api/app/schemas/task_parse.py`
- Create: `apps/api/app/services/task_parser.py`
- Create: `apps/api/app/api/routes/parse.py`
- Modify: `apps/api/app/main.py`
- Test: `apps/api/tests/test_parse_route.py`

**Step 1: Write the failing test**

```python
def test_parse_route_extracts_deadline_duration_and_title(client):
    r = client.post("/api/parse", json={"text": "周五前完成路演PPT，大概3小时"})
    assert r.status_code == 200
    data = r.json()
    assert data["title"] == "路演PPT"
    assert data["duration_minutes"] == 180
    assert data["missing_fields"] == []
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_parse_route.py -v`
Expected: FAIL (route not found).

**Step 3: Write minimal implementation**

```python
class ParseResult(BaseModel):
    title: str
    deadline: datetime | None = None
    duration_minutes: int | None = None
    priority: str = "normal"
    missing_fields: list[str] = []
```

Implement rule-first parser (regex/dateparser) and reserve LLM adapter interface (`LLMParserProtocol`) for future replacement.

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_parse_route.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/schemas apps/api/app/services apps/api/app/api apps/api/tests/test_parse_route.py
git commit -m "feat: add structured task parse endpoint"
```

---

### Task 4: Clarification state machine (max 2 rounds)

**Files:**
- Create: `apps/api/app/services/clarification.py`
- Create: `apps/api/app/api/routes/intake.py`
- Test: `apps/api/tests/test_clarification_flow.py`

**Step 1: Write the failing test**

```python
def test_intake_stops_after_two_clarifications(client):
    r1 = client.post("/api/intake", json={"text": "做个方案", "session_id": "s1"})
    assert r1.json()["action"] == "ask"

    r2 = client.post("/api/intake", json={"text": "尽快", "session_id": "s1"})
    assert r2.json()["action"] == "ask"

    r3 = client.post("/api/intake", json={"text": "不知道多久", "session_id": "s1"})
    assert r3.json()["action"] == "schedule"
    assert r3.json()["task"]["duration_minutes"] == 60
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_clarification_flow.py -v`
Expected: FAIL (endpoint missing).

**Step 3: Write minimal implementation**

```python
MAX_CLARIFY_ROUNDS = 2
REQUIRED_FIELDS = ["deadline", "duration_minutes"]
DEFAULTS = {"duration_minutes": 60, "priority": "normal", "splittable": True}
```

Persist clarification state by `session_id` in DB table `intake_sessions`.

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_clarification_flow.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/services/clarification.py apps/api/app/api/routes/intake.py apps/api/tests/test_clarification_flow.py
git commit -m "feat: implement max-2-round clarification flow"
```

---

### Task 5: Deterministic scheduler service

**Files:**
- Create: `apps/api/app/services/scheduler.py`
- Create: `apps/api/app/api/routes/schedule.py`
- Test: `apps/api/tests/test_scheduler.py`

**Step 1: Write the failing test**

```python
def test_scheduler_avoids_existing_events_and_splits_blocks():
    task = {"title": "路演PPT", "duration_minutes": 180, "deadline": "2026-03-10T18:00:00+08:00"}
    busy = [{"start": "2026-03-08T09:00:00+08:00", "end": "2026-03-08T11:00:00+08:00"}]
    blocks = schedule_task(task, busy, work_window=("09:00", "18:00"))
    assert sum(b["duration_minutes"] for b in blocks) == 180
    assert all(not overlaps(b, busy[0]) for b in blocks)
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_scheduler.py -v`
Expected: FAIL (function undefined).

**Step 3: Write minimal implementation**

```python
def schedule_task(task, busy_events, work_window):
    # 1) build free slots 2) prioritize earliest feasible slot before deadline
    # 3) split into 25-120 minute blocks 4) return deterministic blocks
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_scheduler.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/services/scheduler.py apps/api/app/api/routes/schedule.py apps/api/tests/test_scheduler.py
git commit -m "feat: add deterministic task scheduler"
```

---

### Task 6: Google Calendar provider adapter

**Files:**
- Create: `apps/api/app/integrations/calendar/base.py`
- Create: `apps/api/app/integrations/calendar/google.py`
- Create: `apps/api/app/api/routes/calendar.py`
- Test: `apps/api/tests/test_calendar_google_adapter.py`

**Step 1: Write the failing test**

```python
def test_google_adapter_maps_internal_block_to_google_event(mocker):
    adapter = GoogleCalendarAdapter(token="t")
    mock = mocker.patch("app.integrations.calendar.google.build")
    adapter.create_event("cal_1", {"title": "路演PPT", "start": "2026-03-08T14:00:00+08:00", "end": "2026-03-08T15:00:00+08:00"})
    body = mock.return_value.events.return_value.insert.call_args.kwargs["body"]
    assert body["summary"] == "路演PPT"
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_calendar_google_adapter.py -v`
Expected: FAIL (adapter missing).

**Step 3: Write minimal implementation**

```python
class CalendarProvider(Protocol):
    def create_event(self, calendar_id: str, event: dict) -> str: ...
    def list_busy(self, calendar_id: str, start: datetime, end: datetime) -> list[dict]: ...
```

Implement `GoogleCalendarAdapter` using official Google Calendar API client.

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_calendar_google_adapter.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/integrations/calendar apps/api/app/api/routes/calendar.py apps/api/tests/test_calendar_google_adapter.py
git commit -m "feat: add google calendar provider adapter"
```

---

### Task 7: Replanner async job (unfinished task auto-reschedule)

**Files:**
- Create: `apps/api/app/workers/celery_app.py`
- Create: `apps/api/app/workers/replanner_job.py`
- Test: `apps/api/tests/test_replanner_job.py`

**Step 1: Write the failing test**

```python
def test_replanner_moves_overdue_task_to_next_free_slot(db_session):
    task = create_overdue_task(db_session)
    run_replanner_for_user(task.user_id)
    updated = get_task_blocks(db_session, task.id)
    assert len(updated) > 0
    assert all(b.start > now_utc() for b in updated)
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/test_replanner_job.py -v`
Expected: FAIL (job missing).

**Step 3: Write minimal implementation**

```python
@celery_app.task
def run_replanner_for_user(user_id: str):
    # load overdue tasks -> schedule_task -> upsert new blocks -> enqueue calendar sync
```

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/test_replanner_job.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/app/workers apps/api/tests/test_replanner_job.py
git commit -m "feat: add async replanner job for overdue tasks"
```

---

### Task 8: Web intake chat + schedule preview page

**Files:**
- Create: `apps/web/app/intake/page.tsx`
- Create: `apps/web/components/ChatInput.tsx`
- Create: `apps/web/components/SchedulePreview.tsx`
- Create: `apps/web/lib/api.ts`
- Test: `apps/web/tests/intake.spec.ts`

**Step 1: Write the failing test**

```ts
import { test, expect } from '@playwright/test';

test('user can submit text and see schedule preview', async ({ page }) => {
  await page.goto('/intake');
  await page.fill('[data-testid="chat-input"]', '周五前完成路演PPT，大概3小时');
  await page.click('[data-testid="chat-send"]');
  await expect(page.locator('[data-testid="schedule-preview"]')).toBeVisible();
});
```

**Step 2: Run test to verify it fails**

Run: `pnpm --dir apps/web test:e2e --grep "schedule preview"`
Expected: FAIL (page/components missing).

**Step 3: Write minimal implementation**

```tsx
// intake page: call /api/intake, then /api/schedule, render preview cards
```

**Step 4: Run test to verify it passes**

Run: `pnpm --dir apps/web test:e2e --grep "schedule preview"`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/web/app/intake apps/web/components apps/web/lib apps/web/tests/intake.spec.ts
git commit -m "feat: add intake chat and schedule preview ui"
```

---

### Task 9: End-to-end API integration tests for MVP contract

**Files:**
- Create: `apps/api/tests/e2e/test_mvp_flow.py`
- Modify: `apps/api/tests/conftest.py`

**Step 1: Write the failing test**

```python
def test_mvp_flow_parse_clarify_schedule_sync(client, mock_calendar):
    r = client.post('/api/intake', json={'session_id': 's100', 'text': '做路演PPT'})
    assert r.json()['action'] == 'ask'

    r = client.post('/api/intake', json={'session_id': 's100', 'text': '周五前，3小时'})
    assert r.json()['action'] == 'schedule'

    task_id = r.json()['task']['id']
    r = client.post(f'/api/calendar/sync/{task_id}')
    assert r.status_code == 200
    assert r.json()['synced'] is True
```

**Step 2: Run test to verify it fails**

Run: `poetry run pytest apps/api/tests/e2e/test_mvp_flow.py -v`
Expected: FAIL (missing integration wiring).

**Step 3: Write minimal implementation**

Wire route dependencies and transaction boundaries so the full flow succeeds.

**Step 4: Run test to verify it passes**

Run: `poetry run pytest apps/api/tests/e2e/test_mvp_flow.py -v`
Expected: PASS.

**Step 5: Commit**

```bash
git add apps/api/tests/e2e/test_mvp_flow.py apps/api/tests/conftest.py apps/api/app
git commit -m "test: add mvp end-to-end api flow coverage"
```

---

### Task 10: Deployment and runbook for MVP release

**Files:**
- Create: `infra/docker-compose.yml`
- Create: `infra/api.Dockerfile`
- Create: `infra/web.Dockerfile`
- Create: `docs/runbooks/mvp-deploy.md`
- Test: `docs/runbooks/mvp-smoke-test.md`

**Step 1: Write the failing test**

Create smoke checklist first (failing by definition until deployed):

```markdown
- [ ] /health returns 200
- [ ] create intake session works
- [ ] schedule preview visible in web
- [ ] sync to test google calendar succeeds
```

**Step 2: Run test to verify it fails**

Run: follow `docs/runbooks/mvp-smoke-test.md`
Expected: At least one check fails before deployment stack exists.

**Step 3: Write minimal implementation**

- Add compose services: `api`, `web`, `postgres`, `redis`, `worker`
- Add env var templates and startup instructions
- Add rollback steps

**Step 4: Run test to verify it passes**

Run: `docker compose -f infra/docker-compose.yml up -d && bash docs/runbooks/mvp-smoke-test.sh`
Expected: All checks PASS.

**Step 5: Commit**

```bash
git add infra docs/runbooks
git commit -m "chore: add mvp deployment stack and smoke runbook"
```

---

## Final Verification Gate

Run all checks before completion:

```bash
poetry run pytest apps/api/tests -v
pnpm --dir apps/web test
pnpm --dir apps/web test:e2e
```

Expected: all PASS.

If any fail: fix before merge, do not claim done.

---

## Notes for execution session

- Execute tasks strictly in order.
- Do not skip failing-test step.
- Keep each commit scoped to one task.
- Request code review with @superpowers:requesting-code-review after Task 5 and Task 10.
