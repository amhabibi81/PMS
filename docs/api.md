# API Reference

Base URL: `/api/v1/`

- Interactive docs (Swagger UI): [/api/docs/](http://localhost:8000/api/docs/)
- ReDoc: [/api/redoc/](http://localhost:8000/api/redoc/)
- OpenAPI schema: [/api/schema/](http://localhost:8000/api/schema/) (downloadable JSON/YAML)

All endpoints require JWT auth (except `auth/register` and `auth/login`).
Send the token as `Authorization: Bearer <access>`.

## Authentication (`/auth/`)

| Method | Path             | Description                       | Auth |
|--------|------------------|-----------------------------------|------|
| POST   | `/auth/register/`| Register a new Member             | open |
| POST   | `/auth/login/`   | Obtain JWT pair (access + refresh)| open |
| POST   | `/auth/refresh/` | Refresh access token              | open |
| GET    | `/auth/me/`      | Current authenticated user        | JWT  |
| PATCH  | `/auth/me/`      | Update own first/last name        | JWT  |

### Login example
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"member","password":"member12345"}'
# => {"access":"...","refresh":"..."}
```

## Projects (`/projects/`)

| Method | Path                              | Description                       | Who                     |
|--------|-----------------------------------|-----------------------------------|-------------------------|
| GET    | `/projects/`                      | List (Admin: all; others: own)    | member                  |
| POST   | `/projects/`                      | Create project                    | Admin/PM                |
| GET    | `/projects/{id}/`                 | Retrieve                          | project member          |
| PATCH  | `/projects/{id}/`                 | Update                            | project manager         |
| DELETE | `/projects/{id}/`                 | Delete                            | project manager         |
| GET    | `/projects/{id}/members/`         | List members                      | project member          |
| POST   | `/projects/{id}/members/`         | Add member `{user, role}`         | project manager         |
| DELETE | `/projects/{id}/members/{uid}/`   | Remove member                     | project manager         |
| GET    | `/projects/{id}/activity/`        | Activity log (last 100)           | project member          |

Filters: `?status=`, `?title=`, `?ordering=due_date`, `?search=`. Pagination: 20/page.

## Tasks (`/tasks/`)

| Method | Path                              | Description                                  | Who                          |
|--------|-----------------------------------|----------------------------------------------|------------------------------|
| GET    | `/tasks/`                         | List (filtered by membership)                | member                       |
| POST   | `/tasks/`                         | Create `{project, title, assignee?, ...}`    | project manager              |
| GET    | `/tasks/{id}/`                    | Retrieve                                     | project member               |
| PATCH  | `/tasks/{id}/`                    | Update                                       | manager or assignee          |
| DELETE | `/tasks/{id}/`                    | Delete                                       | manager                      |
| POST   | `/tasks/{id}/transition/`         | `{status}` -- workflow change                | manager or assignee          |
| POST   | `/tasks/{id}/progress/`           | `{progress}` 0-100                           | manager or assignee          |
| GET    | `/tasks/{id}/comments/`           | List comments                                | project member               |
| POST   | `/tasks/{id}/comments/`           | `{body}`                                     | project member               |
| GET    | `/tasks/{id}/attachments/`        | List attachments                             | project member               |
| POST   | `/tasks/{id}/attachments/`        | Multipart `file=...`                         | project member               |

### Status workflow (enforced server-side)
```
Todo -> InProgress -> Review -> Done
                                  ^
reopen: Done -> InProgress  (others rejected with 400)
```
Setting `Done` forces `progress=100`. `progress` locked at 100 while Done.

Filters: `?status=`, `?priority=`, `?assignee=`, `?due_before=`, `?due_after=`.

## Notifications (`/notifications/`)

| Method | Path                                  | Description             |
|--------|---------------------------------------|-------------------------|
| GET    | `/notifications/`                     | List yours (?unread=true)|
| POST   | `/notifications/{id}/mark-read/`      | Mark one read           |
| POST   | `/notifications/mark-all-read/`       | Mark all read           |

## Reports (`/reports/projects/{id}/`)

| Method | Path                              | Description                              |
|--------|-----------------------------------|------------------------------------------|
| GET    | `.../status-distribution/`        | `{[{status,count},...]}`                 |
| GET    | `.../progress-over-time/?days=30` | `{[{timestamp,project_progress},...]}`   |
| GET    | `.../workload/`                   | `{[{user_id,username,open,overdue},...]}`|
| GET    | `.../overdue/`                    | `{[{task_id,title,assignee,due,days_late},...]}` |
| GET    | `.../summary/`                    | `{progress,total,done,overdue,at_risk,flag}`     |
| GET    | `.../export/?fmt=csv&type=summary`| CSV (StreamingHttpResponse)              |
| GET    | `.../export/?fmt=pdf`             | PDF (WeasyPrint)                         |

`type` for CSV: `status-distribution`, `workload`, `overdue`, `summary`.
`at_risk` = >20% tasks overdue OR projected completion past deadline.
