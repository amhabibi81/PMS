# Requirements

## 1. Overview
A web-based Project Management System (PMS) that lets teams define tasks, assign them to members,
track progress, and produce management reports. The design goal — and the thesis's main
differentiator vs Jira/Trello/Asana — is **simplicity and usability**: a user should reach any task
from the dashboard in at most two clicks.

## 2. Stakeholders & roles
| Role            | Capabilities                                                                                  |
|-----------------|-----------------------------------------------------------------------------------------------|
| Admin           | Everything. Manage users, all projects, system-wide reports.                                  |
| Project Manager | CRUD on own projects; add/remove members; create/assign tasks; view project reports.         |
| Team Member     | View projects they belong to; update status & progress of tasks assigned to them; comment.    |

A user may have different roles in different projects (membership role), but their global role
is the maximum privilege they can be granted in any project.

## 3. Functional requirements

### FR-1 Authentication & authorization
- FR-1.1 Register / login / logout / refresh-token via JWT (simplejwt).
- FR-1.2 Global role assigned per user (Admin / ProjectManager / Member).
- FR-1.3 Per-project role via ProjectMembership (Manager / Member).
- FR-1.4 All endpoints enforce permission classes; unauthenticated → 401, wrong role → 403.

### FR-2 Projects
- FR-2.1 CRUD projects (title, description, start_date, due_date, status).
- FR-2.2 Project statuses: `Planning`, `Active`, `OnHold`, `Completed`, `Archived`.
- FR-2.3 Add/remove members; assign a per-project role to each member.
- FR-2.4 List projects where the requesting user is a member (Member) or all projects (Admin/PM).
- FR-2.5 Per-project computed progress = average of task progress (not stored denormalized).

### FR-3 Tasks
- FR-3.1 CRUD tasks within a project (title, description, priority, due_date, assignee, status).
- FR-3.2 Priorities: `Low`, `Medium`, `High`, `Urgent`.
- FR-3.3 Status workflow: `Todo` → `InProgress` → `Review` → `Done`.
  Illegal transitions (e.g. `Todo` → `Done`) are rejected with HTTP 400 and a clear message.
- FR-3.4 Per-task `progress` integer 0–100. Setting status to `Done` forces progress=100.
- FR-3.5 Comments on tasks (append-only, author = requester, edit own only).
- FR-3.6 File attachments on tasks (filename, size, uploaded_by, created_at; stored in media).
- FR-3.7 Filtering by status, assignee, priority, due_date. Pagination: 20/page.

### FR-4 Kanban board
- FR-4.1 Board view grouped by status columns (Todo, InProgress, Review, Done).
- FR-4.2 Drag & drop between columns updates task status; optimistic UI, rollback on error.
- FR-4.3 Reorder within a column (optional ordering field; not required for MVP — defaults to created_at).

### FR-5 Progress tracking
- FR-5.1 Per-task progress (manual 0–100).
- FR-5.2 Per-project progress = avg(task.progress) computed on read.
- FR-5.3 Activity log: append-only record of actor + verb + target + timestamp for every
  create/update/transition event. Powers the activity feed and the "progress over time" report.

### FR-6 Notifications
- FR-6.1 In-app notifications on: task assigned to user, task due in ≤24h, task overdue.
- FR-6.2 Notification list endpoint with read/unread state.
- FR-6.3 Email sending is **architecture-only** for the thesis (pluggable backend, stubbed in dev)
  — no live email sending required for the demo.

### FR-7 Management reports & dashboard
- FR-7.1 Task status distribution per project (data for pie chart).
- FR-7.2 Project progress over time (data for line chart, from ActivityLog snapshots).
- FR-7.3 Workload per member: open tasks count + overdue count (data for bar chart).
- FR-7.4 Overdue tasks table with days-late.
- FR-7.5 Project summary card: % complete + on-track/at-risk flag.
- FR-7.6 "At risk" definition: >20% of tasks overdue OR projected completion past project deadline.
- FR-7.7 Export: CSV (StreamingHttpResponse) and PDF (WeasyPrint from HTML template).
- FR-7.8 Every chart has a date-range filter; heavy report queries cached 5 minutes.

### FR-8 Internationalization
- FR-8.1 UI strings via i18next; supported locales: `fa` (default, RTL) and `en` (LTR).
- FR-8.2 Layout uses logical CSS properties so RTL flips correctly.

## 4. Non-functional requirements

| ID    | Requirement                                                                                       |
|-------|---------------------------------------------------------------------------------------------------|
| NFR-1 | Simplicity & usability — max 2 clicks from dashboard to any task. Clean, low-density UI.         |
| NFR-2 | Extensible, documented architecture with Mermaid diagrams (ERD, C4, sequences) in `/docs`.       |
| NFR-3 | Dockerized; defense demo = `docker compose up` then ready.                                       |
| NFR-4 | Every DRF endpoint has OpenAPI docs (drf-spectacular) and a pytest test.                         |
| NFR-5 | Backend coverage >80% on services & views (documented in test-report.md).                         |
| NFR-6 | No N+1 queries in list endpoints (select_related / prefetch_related).                            |
| NFR-7 | API-first: all features exposed under `/api/v1/`. Frontend is a pure SPA client.                 |
| NFR-8 | Stack is fixed by the approved proposal — no substitutions.                                       |
| NFR-9 | Conventional Commits for git history; every phase produces matching docs in `/docs`.             |

## 5. User stories

### Authentication
- US-A1 — As a visitor, I want to register and log in so I can use the system.
- US-A2 — As a logged-in user, I want my session to persist and refresh automatically.

### Projects
- US-P1 — As a Project Manager, I want to create a project with a deadline so I can plan work.
- US-P2 — As a Project Manager, I want to add members to my project so they can collaborate.
- US-P3 — As a Team Member, I want to see the list of projects I belong to.
- US-P4 — As an Admin, I want to see all projects in the system.

### Tasks
- US-T1 — As a Project Manager, I want to create a task and assign it to a member.
- US-T2 — As a Team Member, I want to update the status of my assigned task as I work.
- US-T3 — As a Team Member, I want to set my task's progress so the project progress updates.
- US-T4 — As a user, I want to comment on a task to clarify requirements.
- US-T5 — As a user, I want to attach a file to a task for shared reference.
- US-T6 — As a user, I want to be blocked from setting a task to Done while it's still Todo, with a clear error.

### Kanban
- US-K1 — As a user, I want to drag a task across columns to change its status.

### Notifications
- US-N1 — As a Team Member, I want to be notified when a task is assigned to me.
- US-N2 — As a Team Member, I want a reminder when my task is due within 24 hours.

### Reports
- US-R1 — As a Project Manager, I want a pie chart of task statuses in my project.
- US-R2 — As a Project Manager, I want a line chart of project progress over time.
- US-R3 — As a Project Manager, I want to see each member's open/overdue workload.
- US-R4 — As a Project Manager, I want to export the project report to PDF and CSV.
- US-R5 — As a Project Manager, I want an at-a-glance "at risk" flag on each project card.

### Internationalization
- US-I1 — As a Persian-speaking user, I want the UI in Farsi with RTL layout.
- US-I2 — As a user, I want to switch between Farsi and English.

## 6. Out of scope (for thesis MVP)
- Time tracking / logged hours.
- Gantt charts.
- Custom workflow builder (status flow is fixed at Todo→InProgress→Review→Done).
- Subtasks / task hierarchy (single-level tasks only).
- SSO / OAuth / social login.
- Mobile native app (responsive web only).
- Real-time websockets (notifications are polled).
- Custom fields.
