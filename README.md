# Project Management System (PMS)

> A lightweight, self-hostable project management web app — a simpler alternative to Jira, Trello, Asana, and ClickUp. Built as a bachelor thesis project for Amirkabir University of Technology.

The core differentiator is **simplicity and usability**: a clean, low-density UI where any task is reachable from the dashboard in **at most two clicks**, with built-in Persian (Farsi) RTL support and a 1-command Docker setup.

---

## Table of Contents
- [Screenshots](#screenshots)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Repository Layout](#repository-layout)
- [Prerequisites](#prerequisites)
- [Running the Project](#running-the-project)
  - [Option A — Docker (recommended)](#option-a--docker-recommended)
  - [Option B — Local (no Docker)](#option-b--local-no-docker)
- [Demo Walkthrough](#demo-walkthrough)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Default Accounts](#default-accounts)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Documentation](#documentation)
- [Thesis Context](#thesis-context)
- [License](#license)

---

## Screenshots

> Add captured screenshots to [`docs/screenshots/`](docs/screenshots/) before sharing or defending.

| View | Description |
|------|-------------|
| `login.png` | Login screen (Persian RTL) |
| `dashboard.png` | Management dashboard with charts and at-risk badges |
| `kanban.png` | Kanban board with drag & drop |
| `reports.png` | Exported CSV/PDF report or charts close-up |
| `task-detail.png` | Task detail modal (progress slider, comments) |

---

## Features

### Core capabilities
- **Task definition & assignment** — CRUD tasks, assign to project members, set priority and due date.
- **Progress tracking** — per-task progress (0–100%), per-project computed progress (average of tasks), append-only activity log.
- **Management reporting** — dashboard with charts (status distribution, progress over time, workload per member, overdue tasks), plus CSV and PDF export.

### Highlights
- **Kanban board** with drag & drop (Todo → In Progress → Review → Done), optimistic updates with rollback on illegal transitions.
- **Role-based access** — three global roles (Admin, Project Manager, Team Member) plus per-project roles.
- **JWT authentication** with access/refresh token rotation.
- **Notifications** — in-app notifications for task assignment, due-soon, and overdue (email-ready architecture, stubbed backend).
- **Internationalization** — Persian (Farsi, RTL, default) and English (LTR) with one-click language switch.
- **Self-hostable** — the whole stack runs with `docker compose up --build`.
- **Well-tested** — 92% backend coverage (60 tests), 13 frontend integration tests.
- **Documented API** — OpenAPI/Swagger UI, every endpoint has tests.

---

## Tech Stack

| Layer        | Technology |
|--------------|------------|
| **Backend**  | Django 5, Django REST Framework, djangorestframework-simplejwt, django-filter, django-cors-headers, drf-spectacular |
| **Database** | PostgreSQL 16 |
| **Frontend** | React 18 (Vite), TanStack Query, React Router, @dnd-kit, Recharts, react-hook-form + zod, i18next, Tailwind CSS |
| **Auth**     | JWT (simplejwt) |
| **DevOps**   | Docker, docker-compose |
| **Testing**  | pytest + pytest-django + factory_boy (backend), Vitest + React Testing Library + MSW (frontend) |
| **Linting**  | ruff (backend), ESLint (frontend) |

---

## Architecture

```
Browser (React SPA) ──HTTPS+JWT──▶ Django REST Framework (/api/v1/*)
                                         │
                            ┌────────────┴────────────┐
                       services.py                drf-spectacular
                       (business logic)           (OpenAPI schema)
                            │
                       ORM models
                            │
                       PostgreSQL 16
```

**Layering rules:**
- Model → Serializer → Service (business logic) → ViewSet → URL → Test.
- Business logic lives in `services.py`, never in views or serializers.
- N+1 queries avoided with `select_related` / `prefetch_related`.
- Every endpoint has OpenAPI docs and a pytest test.

See [`docs/architecture.md`](docs/architecture.md) for the full C4 diagram and request lifecycle.

---

## Repository Layout

```
.
├── backend/                # Django + DRF API
│   ├── apps/               # one Django app per domain
│   │   ├── accounts/       # users, JWT auth, roles
│   │   ├── projects/       # projects, memberships, activity log
│   │   ├── tasks/          # tasks, comments, attachments
│   │   ├── notifications/  # in-app notifications
│   │   └── reports/        # aggregation endpoints + CSV/PDF export
│   ├── config/             # settings, urls, wsgi/asgi
│   ├── templates/          # PDF report HTML template
│   ├── manage.py
│   ├── requirements.txt
│   └── pytest.ini
├── frontend/               # React + Vite SPA
│   ├── src/
│   │   ├── components/     # shared UI + Layout
│   │   ├── contexts/       # Auth + Toast contexts
│   │   ├── features/       # feature folders (auth, projects, tasks, ...)
│   │   ├── lib/            # axios instance + query client
│   │   ├── locales/        # fa.json, en.json
│   │   └── test/           # MSW handlers + setup
│   ├── Dockerfile
│   └── package.json
├── docs/                   # requirements, ERD, architecture, API, tests
├── docker-compose.yml
└── README.md
```

---

## Prerequisites

**For Docker (recommended):**
- [Docker Desktop](https://www.docker.com/products/docker-desktop) (includes Docker Compose)

**For local run (no Docker):**
- Python 3.12+
- Node.js 20+ (with npm)
- No PostgreSQL needed — falls back to SQLite locally

---

## Running the Project

### Option A — Docker (recommended)

The full stack (Postgres + Django backend + React frontend) starts with one command:

```bash
git clone <your-repo-url> pms
cd pms
docker compose up --build
```

Wait for the first build (~3–5 minutes). On startup the backend automatically:
1. Runs `makemigrations` + `migrate` (creates database schema)
2. Runs `seed_demo` (creates demo users, a sample project, and 4 tasks)
3. Starts the dev server

**Access:**
| Service | URL |
|---------|-----|
| Frontend app | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1/ |
| Swagger UI (API docs) | http://localhost:8000/api/docs/ |
| Django admin | http://localhost:8000/admin/ |

Log in at http://localhost:5173 using one of the [default accounts](#default-accounts).

To stop: `Ctrl+C` in the terminal, then optionally `docker compose down` (add `-v` to also wipe the database volume).

---

### Option B — Local (no Docker)

Run the backend and frontend in two separate terminals. Uses SQLite, so no PostgreSQL setup needed.

**Terminal 1 — Backend:**
```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1            # activate venv (Git Bash: source .venv/bin/activate)
pip install -r requirements.txt

# Bundled SQLite settings (no Postgres required)
$env:DJANGO_SETTINGS_MODULE = "config.settings_local"
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000     # if 8000 is reserved, use 8088 (see Troubleshooting)
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
# If the backend is NOT on 8000, set the port here too:
$env:VITE_BACKEND_PORT = "8000"               # change to "8088" if you used 8088 above
npm run dev
```

Open http://localhost:5173 — the Vite dev server proxies `/api` requests to the backend (default `http://localhost:8000`, or `$VITE_BACKEND_PORT` if set).

> The local-run settings file is [`backend/config/settings_local.py`](backend/config/settings_local.py). It uses SQLite and a local email backend; everything else matches the Docker setup.

---

## Demo Walkthrough

1. **Log in** at http://localhost:5173 as `pm` / `pm12345`.
2. **Dashboard** — per-project cards with charts (status pie, workload bar, progress-over-time line), overdue table, and at-risk badges. Try the CSV/PDF export buttons.
3. **Projects** — click a project card to open its Kanban board.
4. **Kanban** — drag a task across columns (Todo → In Progress → Review → Done). Illegal jumps (e.g. Todo → Done) are rejected with a toast and rolled back. Click a task to open its detail: set progress, change status, comment, attach a file.
5. **Notifications** — the bell badge in the nav shows unread count; mark read there.
6. **Language** — toggle فا / EN in the top nav; the layout flips between RTL and LTR.

Log in as `member` / `member12345` to see the restricted Team Member view (only the project they belong to; can update their own tasks only).

---

## API Reference

Base URL: `/api/v1/` (all endpoints require JWT except `auth/register` and `auth/login`).

Interactive docs:
- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI schema:** http://localhost:8000/api/schema/

### Quick reference

| Group | Endpoints |
|-------|-----------|
| **Auth** | `POST /auth/register/`, `POST /auth/login/`, `POST /auth/refresh/`, `GET/PATCH /auth/me/` |
| **Projects** | `GET/POST /projects/`, `GET/PATCH/DELETE /projects/{id}/`, `GET/POST /projects/{id}/members/`, `DELETE /projects/{id}/members/{user_id}/`, `GET /projects/{id}/activity/` |
| **Tasks** | `GET/POST /tasks/`, `GET/PATCH/DELETE /tasks/{id}/`, `POST /tasks/{id}/transition/`, `POST /tasks/{id}/progress/`, `GET/POST /tasks/{id}/comments/`, `GET/POST /tasks/{id}/attachments/` |
| **Notifications** | `GET /notifications/`, `POST /notifications/{id}/mark-read/`, `POST /notifications/mark-all-read/` |
| **Reports** | `GET /reports/projects/{id}/{status-distribution|progress-over-time|workload|overdue|summary}/`, `GET /reports/projects/{id}/export/?fmt=csv\|pdf&type=...` |

Full details with examples: [`docs/api.md`](docs/api.md).

### Example: login + use the API
```bash
# Get JWT tokens
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"pm","password":"pm12345"}' | jq -r .access)

# List projects
curl -s http://localhost:8000/api/v1/projects/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## Testing

### Backend (pytest)
```bash
docker compose run --rm backend pytest                         # run all
docker compose run --rm backend pytest --cov=apps              # with coverage
docker compose run --rm backend pytest apps/tasks/tests/       # one app
```

**60 tests, 92% total coverage.** Services at 100%, views at 85–92%.

### Frontend (Vitest)
```bash
cd frontend && npm test      # run once
cd frontend && npm run test:watch   # watch mode
```

**13 tests** across 5 suites (auth, projects, Kanban rollback, notifications).

### Other
```bash
docker compose run --rm backend ruff check backend/    # lint backend
cd frontend && npm run lint                            # lint frontend
cd frontend && npm run build                           # production build
```

See [`docs/test-report.md`](docs/test-report.md) for the full coverage breakdown.

---

## Default Accounts

Seeded automatically on first run (Docker `seed_demo` command or local `python manage.py seed_demo`).

| Role            | Username | Password     | Capabilities |
|-----------------|----------|--------------|--------------|
| Admin           | `admin`  | `admin12345` | Everything, all projects, system-wide |
| Project Manager | `pm`     | `pm12345`    | Create/edit own projects, assign tasks, view reports |
| Team Member     | `member` | `member12345`| View assigned projects, update own tasks, comment |

> ⚠️ **Change these passwords before any real deployment.** They exist only for the demo.

---

## Configuration

Environment variables (set in `docker-compose.yml` or `backend/.env`):

| Variable | Default | Purpose |
|----------|---------|---------|
| `DJANGO_DEBUG` | `True` | Django debug mode |
| `DJANGO_SECRET_KEY` | `dev-insecure-change-me` | Django secret key (change in production!) |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,backend` | Allowed HTTP hosts |
| `POSTGRES_DB` | `pms` | Database name |
| `POSTGRES_USER` | `pms` | Database user |
| `POSTGRES_PASSWORD` | `pms12345` | Database password (change in production!) |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Frontend origin(s) |
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | API base URL for the frontend |

---

## Troubleshooting

**Port already in use (5173 / 5432 / 8000):** stop the conflicting process, or change the port mapping in `docker-compose.yml`.

**`Error: You don't have permission to access that port` on Windows (local run):** Windows (often via Hyper-V / WSL2) reserves ranges of TCP ports that apps cannot bind to -- port 8000 is a common victim. Check the reserved ranges:
```
netsh interface ipv4 show excludedportrange protocol=tcp
```
If `8000` is inside any listed range, run the backend on a free port (e.g. `8088`) and tell the frontend about it:
```powershell
# Terminal 1 (backend)
$env:DJANGO_SETTINGS_MODULE = "config.settings_local"
python manage.py runserver 127.0.0.1:8088
# Terminal 2 (frontend)
$env:VITE_BACKEND_PORT = "8088"
npm run dev
```
(To permanently free a reserved range you can disable Hyper-V autostart and reboot, but using an alternate port is the simpler fix.)

**`.venv\Scripts\Activate.ps1` errors with "running scripts is disabled":** PowerShell's execution policy blocks the activate script. Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then retry. Or skip activation and call `.venv\Scripts\python.exe` and `.venv\Scripts\pip.exe` directly.

**`ModuleNotFoundError: No module named 'django'` after install:** the venv wasn't activated when `pip install` ran. Either activate first, or install explicitly into the venv: `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

**Backend container fails to start:** check logs with `docker compose logs backend`. Most often a missing env var or a port conflict with another Postgres.

**Persian fonts not rendering (local LaTeX / reports):** the PDF export uses WeasyPrint; on Linux containers it needs system fonts. The Docker image already installs them.

**`npm install` is slow / fails:** ensure Node 20+, clear cache with `npm cache clean --force`, retry.

**Cannot log in after changing DB:** re-run `docker compose run --rm backend python manage.py seed_demo` to recreate the demo users.

---

## Documentation

All documentation lives in [`docs/`](docs/) and renders on GitHub:

- [**Requirements**](docs/requirements.md) — functional/non-functional requirements and user stories
- [**ERD**](docs/erd.md) — entity-relationship diagram (Mermaid)
- [**Architecture**](docs/architecture.md) — C4 component diagram + request lifecycle
- [**API reference**](docs/api.md) — every endpoint with examples
- [**Sequence diagrams**](docs/sequence-diagrams.md) — login, task assignment, report generation
- [**Test report**](docs/test-report.md) — coverage tables and test discipline
- [**Comparison**](docs/comparison.md) — PMS vs Jira/Trello/Asana/ClickUp (thesis justification)
- [**Docs index**](docs/README.md)

---

## Thesis Context

This project is the implementation half of a bachelor thesis at Amirkabir University of Technology (Department of Computer Engineering). The thesis argues that small teams are better served by a **simple, focused, RTL-capable, self-hostable** tool than by feature-heavy commercial alternatives.

The full justification is in [`docs/comparison.md`](docs/comparison.md).

---

## License

This project is submitted as part of a bachelor thesis. Licensing terms, if any, are at the discretion of the author and Amirkabir University of Technology.
