# Documentation Index

All project documentation lives here. This index is the entry point for a thesis
reviewer or new contributor.

## By phase

| Phase | Document | Purpose |
|-------|----------|---------|
| 1 | [requirements.md](requirements.md) | Functional & non-functional requirements, user stories, out-of-scope |
| 2 | [erd.md](erd.md) | Entity-Relationship Diagram (Mermaid) + design notes |
| 2 | [architecture.md](architecture.md) | C4 component diagram, request lifecycle, layering rules |
| 3 | [api.md](api.md) | REST API reference (every endpoint, auth, examples) |
| 3 | [sequence-diagrams.md](sequence-diagrams.md) | Mermaid sequences: login, task assignment, report generation |
| 5 | [test-report.md](test-report.md) | Coverage tables, business-rule coverage, test discipline |
| 6 | [comparison.md](comparison.md) | PMS vs Jira/Trello/Asana/ClickUp -- the thesis justification |

## Quick links for the defense

- **One-command demo:** `docker compose up --build` (see root [README](../README.md))
- **API explorer (Swagger):** http://localhost:8000/api/docs/
- **ERD (for the report):** [erd.md](erd.md) -- renders on GitHub
- **Architecture (for the report):** [architecture.md](architecture.md)
- **Why this project exists:** [comparison.md](comparison.md)

## Conventions
- All diagrams are Mermaid (renderable on GitHub and exportable to the report).
- Cross-references use relative links so docs work offline.
- English prose; key sections can be translated to Persian for the final report.
- Each doc is updated in the same session as the code change it describes.
