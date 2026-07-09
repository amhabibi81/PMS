# Architecture

## C4-style component diagram (Mermaid)

```mermaid
flowchart LR
    subgraph Browser["User's browser"]
        UI["React SPA<br/>Vite + TanStack Query<br/>+ @dnd-kit + Recharts + i18next"]
    end

    subgraph Docker["docker compose"]
        subgraph Backend["Backend container"]
            DRF["Django REST Framework<br/>/api/v1/*"]
            JWT["SimpleJWT auth"]
            SPEC["drf-spectacular<br/>OpenAPI schema"]
            SVC["services.py<br/>business logic"]
            MODELS["Django ORM models"]
        end
        subgraph DB["db container"]
            PG[("PostgreSQL 16")]
        end
        subgraph FE["frontend container"]
            VITE["Vite dev server<br/>:5173"]
        end
    end

    UI -->|HTTPS + JWT| DRF
    DRF --> JWT
    DRF --> SVC
    SVC --> MODELS
    MODELS --> PG
    SPEC -.reads.-> DRF
    VITE -.serves.-> UI
```

## Request lifecycle (typical: "list tasks on a project")

```mermaid
sequenceDiagram
    autonumber
    participant U as User (browser)
    participant R as React SPA
    participant A as DRF API (/api/v1/)
    participant S as services.py
    participant DB as PostgreSQL

    U->>R: Open Kanban board
    R->>A: GET /api/v1/projects/{id}/tasks/ (JWT)
    A->>A: JWTAuthentication -> request.user
    A->>A: IsAuthenticated + ProjectMemberPermission
    A->>S: list_tasks(project, user, filters)
    S->>DB: SELECT ... FROM tasks WHERE project_id=? (filtered, paginated)
    DB-->>S: rows
    S-->>A: queryset + summary
    A-->>R: 200 JSON (paginated)
    R-->>U: Render Kanban columns
```

## Layers & rules

| Layer            | Responsibility                                                | Where                                  |
|------------------|---------------------------------------------------------------|----------------------------------------|
| Presentation     | HTTP, serialization, pagination, permissions                  | DRF viewsets, `apps/*/views.py`        |
| Service          | Business logic (status transitions, progress, reports)       | `apps/*/services.py`                   |
| Domain/Model     | Data + invariants + computed properties                        | `apps/*/models.py`                     |
| Persistence      | ORM, migrations, indexes                                      | Django ORM + `apps/*/migrations/`      |
| Infra            | DB, cache, email backend (stubbed)                            | `config/settings.py`                   |

Rules (from the django-api skill):
- Model → Serializer → Service → ViewSet → URL → Test. Always in this order.
- Business logic lives in `services.py`, never in views or serializers.
- N+1 queries avoided with `select_related`/`prefetch_related`.
- Every endpoint has OpenAPI docs (drf-spectacular) and a pytest test.

## Why these choices (thesis justification)

- **API-first** — frontend is a pure SPA; the same API serves the demo and any future mobile client.
- **Fat models / thin views / services for logic** — keeps each layer testable and explainable.
- **LocMem cache + stubbed email** — thesis demo needs no external services beyond Postgres.
- **Docker** — defense demo is `docker compose up` and ready.
