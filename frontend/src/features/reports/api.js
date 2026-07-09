import api from "../../lib/api";

export const reportsApi = {
  statusDistribution: (projectId) => api.get(`/reports/projects/${projectId}/status-distribution/`).then((r) => r.data),
  progressOverTime: (projectId, days = 30) =>
    api.get(`/reports/projects/${projectId}/progress-over-time/`, { params: { days } }).then((r) => r.data),
  workload: (projectId) => api.get(`/reports/projects/${projectId}/workload/`).then((r) => r.data),
  overdue: (projectId) => api.get(`/reports/projects/${projectId}/overdue/`).then((r) => r.data),
  summary: (projectId) => api.get(`/reports/projects/${projectId}/summary/`).then((r) => r.data),
  exportUrl: (projectId, fmt, type) =>
    `/api/v1/reports/projects/${projectId}/export/?fmt=${fmt}${type ? `&type=${type}` : ""}`,
};
