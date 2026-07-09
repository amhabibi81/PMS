# Comparison: PMS vs Existing Tools

This document is the core justification for the thesis. The project's stated
differentiator is **simplicity and usability** -- this table shows where the
PMS deliberately trades feature breadth for clarity, and why that trade is
defensible for small teams.

## At a glance

| Feature                                  | **PMS** | Jira | Trello | Asana | ClickUp |
|------------------------------------------|:-------:|:----:|:------:|:-----:|:-------:|
| Task CRUD + assignment                   | yes     | yes  | yes    | yes   | yes     |
| Kanban with drag & drop                  | yes     | yes  | yes    | yes   | yes     |
| Fixed simple status workflow             | yes     | no*  | no*    | no*   | no*     |
| Computed project progress                | yes     | yes  | no     | yes   | yes     |
| Management dashboard (charts)            | yes     | yes  | add-on | yes   | yes     |
| CSV / PDF export                         | yes     | yes  | add-on | yes   | yes     |
| Role-based access (Admin/PM/Member)      | yes     | yes  | paid   | yes   | yes     |
| Persian (RTL) UI built-in                | yes     | no   | no     | no    | no      |
| Self-hostable (Docker, 1 command)        | yes     | no   | no     | no    | no      |
| Custom fields                            | no      | yes  | yes    | yes   | yes     |
| Configurable workflows / statuses        | no      | yes  | yes    | yes   | yes     |
| Time tracking / logged hours             | no      | yes  | add-on | paid  | yes     |
| Gantt charts                             | no      | yes  | add-on | paid  | yes     |
| Subtasks / task hierarchy                | no      | yes  | yes    | yes   | yes     |
| SSO / OAuth / SAML                       | no      | yes  | yes    | yes   | yes     |
| Marketplace / plugins                    | no      | yes  | yes    | yes   | yes     |

\* Jira/Trello/Asana/ClickUp allow *configurable* workflows, which is more
powerful but also more complex to set up and learn. PMS fixes the workflow at
`Todo -> In Progress -> Review -> Done` intentionally (see FR-3.3).

## Design principles and how they show up

### 1. Simplicity over configurability
Existing tools optimize for "can do anything," which means days of setup and a
steep learning curve. PMS ships with **one fixed, sensible workflow** and one
role model. The cost: teams with unusual processes must adapt. The benefit: a
new team is productive in minutes, not days. For small teams and student
projects -- the thesis's target audience -- this is the right trade.

Evidence in the codebase:
- Status transitions are validated in [tasks/services.py](../backend/apps/tasks/services.py)
  (`Task.TRANSITIONS`) -- illegal jumps return HTTP 400. No workflow editor.
- The permission model is three roles + per-project role
  ([projects/permissions.py](../backend/apps/projects/permissions.py)). No
  permission-scheme matrix to configure.

### 2. Usability: max 2 clicks to any task
From the dashboard, a user clicks a project card (1) then any task on the
Kanban board (2) and is in the task detail. This is enforced as a design rule
in the react-frontend skill and visible in the routing
([App.jsx](../frontend/src/App.jsx)): `/dashboard`, `/projects`, `/projects/:id`.

By contrast, locating a task in Jira typically requires: open project -> select
board or backlog -> apply filters -> open issue -- often 3-4+ clicks and
several UI layers.

### 3. Built-in RTL / Persian
Jira, Trello, Asana, and ClickUp do not ship a Persian RTL UI. For an
Iranian student team or small local business, this is a real barrier. PMS is
i18n-first with `fa` (RTL) as the default locale
([locales/fa.json](../frontend/src/locales/fa.json), [i18n.js](../frontend/src/i18n.js))
and toggles direction on the `<html>` element via logical CSS properties.

### 4. Self-hostable, transparent, defensible
The whole system runs with `docker compose up` and is fully open in the repo.
A thesis reviewer can read every line, run it locally, and audit the
architecture diagrams. Cloud-only tools are black boxes by comparison.

### 5. Management reporting without the enterprise price
Status distribution, progress-over-time, workload-per-member, overdue tasks,
and at-risk flags are all built in and exportable to CSV/PDF
([reports/services.py](../backend/apps/reports/services.py)). In Trello these
require paid power-ups; in Jira they require admin configuration.

## What PMS deliberately does NOT do (and why that's fine)

| Out of scope        | Why it's excluded for this thesis                                                                                                |
|---------------------|----------------------------------------------------------------------------------------------------------------------------------|
| Custom fields       | Adds schema complexity and UI clutter. Small teams rarely need them; when they do, the description field suffices.              |
| Configurable statuses | A fixed workflow is teachable and testable. Custom workflows multiply edge cases (transitions, permissions, reports).          |
| Time tracking       | Requires timers, approval flows, and reporting -- a separate product surface. Out of scope for an MVP.                          |
| Gantt charts        | Render complexity and dependencies that the fixed workflow doesn't model.                                                       |
| Subtasks            | Hierarchy complicates progress computation and permissions. Single-level tasks keep the model explainable.                      |
| SSO / OAuth         | JWT auth is sufficient and defensible. Enterprise SSO is its own integration surface.                                            |
| Plugins / marketplace | A plugin system is a thesis of its own. The architecture is extensible (services layer, app-per-domain) without one.          |

## Summary

PMS is not competing with Jira on features. It competes on **clarity, speed of
onboarding, RTL support, and self-hostability**. For a small team that wants
project management without a two-day setup workshop and an English-only UI,
PMS is the right tool -- and that is the thesis's claim.
