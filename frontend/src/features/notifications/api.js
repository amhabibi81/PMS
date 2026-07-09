import api from "../../lib/api";

export const notificationsApi = {
  list: (params) => api.get("/notifications/", { params }).then((r) => r.data),
  markRead: (id) => api.post(`/notifications/${id}/mark-read/`).then((r) => r.data),
  markAllRead: () => api.post("/notifications/mark-all-read/").then((r) => r.data),
};
