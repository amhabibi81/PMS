import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";

export const handlers = [
  http.post("/api/v1/auth/login/", async ({ request }) => {
    const body = await request.json();
    if (body.username === "member" && body.password === "member12345") {
      return HttpResponse.json({ access: "a", refresh: "r" });
    }
    return new HttpResponse(null, { status: 401 });
  }),
  http.post("/api/v1/auth/register/", async ({ request }) => {
    const body = await request.json();
    if (body.username === "taken") {
      return HttpResponse.json(
        { username: ["A user with that username already exists."] },
        { status: 400 }
      );
    }
    return HttpResponse.json({
      id: 9, username: body.username, email: body.email, role: "Member",
    }, { status: 201 });
  }),
  http.get("/api/v1/auth/me/", ({ request }) => {
    if (request.headers.get("Authorization") === "Bearer a") {
      return HttpResponse.json({ id: 1, username: "member", role: "Member" });
    }
    return new HttpResponse(null, { status: 401 });
  }),
  http.get("/api/v1/projects/", () =>
    HttpResponse.json({
      results: [
        { id: 1, title: "Demo", description: "x", status: "Active", progress: 50, members_count: 2, tasks_count: 4 },
      ],
    })
  ),
  http.post("/api/v1/projects/", async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({ id: 2, ...body, status: "Active", progress: 0, members_count: 1, tasks_count: 0 }, { status: 201 });
  }),
  http.get("/api/v1/notifications/", () =>
    HttpResponse.json({
      results: [
        { id: 1, type: "TASK_ASSIGNED", message: "You got a task", is_read: false, created_at: "2026-07-09T10:00:00Z" },
        { id: 2, type: "OVERDUE", message: "Late", is_read: true, created_at: "2026-07-09T09:00:00Z" },
      ],
    })
  ),
  http.post("/api/v1/notifications/:id/mark-read/", ({ params }) =>
    HttpResponse.json({ id: Number(params.id), is_read: true, type: "TASK_ASSIGNED", message: "x", created_at: "2026-07-09T10:00:00Z" })
  ),
  http.post("/api/v1/notifications/mark-all-read/", () =>
    HttpResponse.json({ marked_read: 1 })
  ),
  http.get("/api/v1/tasks/", ({ request }) => {
    const url = new URL(request.url);
    if (url.searchParams.get("project") === "1") {
      return HttpResponse.json({
        results: [
          { id: 1, title: "Task A", status: "Todo", priority: "Medium", progress: 0, project: 1 },
          { id: 2, title: "Task B", status: "Todo", priority: "High", progress: 0, project: 1 },
        ],
      });
    }
    return HttpResponse.json({ results: [] });
  }),
  http.post("/api/v1/tasks/:id/transition/", async ({ request, params }) => {
    const body = await request.json();
    if (body.status === "Done" && params.id === "1") {
      return HttpResponse.json(
        { detail: "Illegal status transition: Todo -> Done" },
        { status: 400 }
      );
    }
    return HttpResponse.json({ id: Number(params.id), status: body.status, title: "T", priority: "Medium", progress: 0 });
  }),
];

export const server = setupServer(...handlers);
