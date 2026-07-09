# Test Report

This report summarizes the test coverage for the PMS project. It is intended as
supporting material for the thesis document and defense.

## Tooling

| Layer    | Framework                     | Mocking        |
|----------|-------------------------------|----------------|
| Backend  | pytest + pytest-django        | factory_boy    |
| Frontend | Vitest + React Testing Library| MSW (API mock) |

## How to run

```bash
# Backend (inside the backend container or a venv with deps installed)
docker compose run --rm backend pytest --cov=apps --cov-report=term

# Frontend
cd frontend && npm test
```

## Backend coverage

**Total: 92% (60 tests passing)** -- exceeds the >80% target on services and views.

### Per-file coverage (key files)

| File                            | Coverage | Tests |
|---------------------------------|---------:|-------|
| accounts/views.py               | 100%     | 6     |
| accounts/serializers.py         | 100%     | -     |
| accounts/models.py              | 96%      | -     |
| notifications/services.py       | 100%     | 2     |
| notifications/views.py          | 100%     | 4     |
| notifications/serializers.py    | 100%     | -     |
| projects/services.py            | 100%     | 4     |
| projects/views.py               | 88%      | 7     |
| projects/serializers.py         | 100%     | -     |
| projects/models.py              | 96%      | -     |
| tasks/services.py               | 100%     | 7     |
| tasks/views.py                  | 92%      | 8     |
| tasks/serializers.py            | 94%      | -     |
| tasks/permissions.py            | 88%      | -     |
| reports/services.py             | 97%      | -     |
| reports/views.py                | 85%      | 6     |

### Business rules covered by tests

- Task status workflow: legal transitions succeed; illegal jumps (Todo -> Done)
  rejected with HTTP 400.
- Setting status to `Done` forces `progress = 100`; progress locked at 100 while Done.
- Reopen: `Done -> InProgress` allowed.
- Project progress is computed (average of task progress), never stored denormalized.
- At-risk logic: >20% overdue OR projected completion past deadline -> `at_risk = true`.
- Permissions: Member cannot create projects/tasks (403); non-member cannot read (404);
  assignee can update own task; PM can add/remove members; Admin sees all.
- CSV export works for every report type; invalid `fmt` returns 400.
- ActivityLog records PROJECT_CREATED/UPDATED, MEMBER_ADDED/REMOVED,
  TASK_CREATED/UPDATED/STATUS_CHANGED/PROGRESS_CHANGED/ASSIGNED, COMMENT_ADDED,
  ATTACHMENT_UPLOADED.
- Notifications: per-user scoping, unread filter, mark-read, mark-all-read.

## Frontend coverage

**13 tests passing across 5 suites** -- `npm run build` succeeds.

| Suite                    | Tests | What it verifies |
|--------------------------|------:|------------------|
| auth/Login               | 3     | validation on empty fields, error toast on wrong creds, successful login stores JWT |
| auth/Register            | 3     | short-password error, invalid-email error, duplicate-username server error toast |
| projects/ProjectList     | 2     | lists projects from API, create-modal flow submits and closes |
| tasks/KanbanBoard        | 2     | renders columns/tasks, **optimistic rollback toast on illegal transition** |
| notifications/NotificationList | 3 | renders badges, per-row mark-read, mark-all-read |

### Key behaviors covered

- Form validation (zod) shows inline errors; submit disabled while pending.
- Kanban optimistic update rolls back on API error with a clear toast
  (the react-frontend skill's required pattern).
- API calls are mocked with MSW so tests are deterministic and network-free.

## Known coverage gaps (acceptable for thesis scope)

- `reports/serializers.py` is 0% -- these are DRF Serializer classes used only as
  schema annotations; the report endpoints return raw dicts and are fully tested
  through the views. Low value to test directly.
- `projects/permissions.py` ProjectMemberMixin helper (48%) -- the nested-resource
  helper is exercised indirectly through the membership endpoints; the explicit
  `permission_denied` branch is not hit.
- PDF export branch in `reports/views.py` -- WeasyPrint is import-guarded; the
  happy path requires a real PDF render which is environment-dependent. The CSV
  branch and the 503 (missing WeasyPrint) branch are covered.

## Test discipline (process)

Following the testing skill:
1. Tests are run after every feature and before every commit.
2. When a bug is found, the failing test is written **first**, then the fix.
3. Each endpoint has at least: happy path, 401 (unauthenticated), 403 (wrong role),
   400 (validation), 404 (non-member/not-found) where applicable.
