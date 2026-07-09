import api from "../../lib/api";

export const projectsApi = {
  list: (params) => api.get("/projects/", { params }).then((r) => r.data),
  get: (id) => api.get(`/projects/${id}/`).then((r) => r.data),
  create: (data) => api.post("/projects/", data).then((r) => r.data),
  update: (id, data) => api.patch(`/projects/${id}/`, data).then((r) => r.data),
  remove: (id) => api.delete(`/projects/${id}/`),
  members: (id) => api.get(`/projects/${id}/members/`).then((r) => r.data),
  addMember: (id, data) => api.post(`/projects/${id}/members/`, data).then((r) => r.data),
  removeMember: (id, userId) => api.delete(`/projects/${id}/members/${userId}/`),
  activity: (id) => api.get(`/projects/${id}/activity/`).then((r) => r.data),
};
