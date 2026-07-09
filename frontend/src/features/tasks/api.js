import api from "../../lib/api";

export const tasksApi = {
  list: (params) => api.get("/tasks/", { params }).then((r) => r.data),
  get: (id) => api.get(`/tasks/${id}/`).then((r) => r.data),
  create: (data) => api.post("/tasks/", data).then((r) => r.data),
  update: (id, data) => api.patch(`/tasks/${id}/`, data).then((r) => r.data),
  transition: (id, status) => api.post(`/tasks/${id}/transition/`, { status }).then((r) => r.data),
  progress: (id, value) => api.post(`/tasks/${id}/progress/`, { progress: value }).then((r) => r.data),
  comments: (id) => api.get(`/tasks/${id}/comments/`).then((r) => r.data),
  addComment: (id, body) => api.post(`/tasks/${id}/comments/`, { body }).then((r) => r.data),
  attachments: (id) => api.get(`/tasks/${id}/attachments/`).then((r) => r.data),
  uploadAttachment: (id, file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post(`/tasks/${id}/attachments/`, form, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data);
  },
};
