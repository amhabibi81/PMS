import { useTranslation } from "react-i18next";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "./api";
import { Badge } from "../../components/ui/Badge";
import { EmptyState, LoadingState } from "../../components/ui/states";
import { useToast } from "../../contexts/ToastContext";

export default function NotificationList() {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list(),
  });

  const markRead = useMutation({
    mutationFn: notificationsApi.markRead,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications"] }),
  });
  const markAll = useMutation({
    mutationFn: notificationsApi.markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      toast.success(t("notification.markAllRead"));
    },
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("notification.title")}</h1>
        <button onClick={() => markAll.mutate()} className="btn-secondary">{t("notification.markAllRead")}</button>
      </div>
      {isLoading ? (
        <LoadingState />
      ) : (data?.results || []).length === 0 ? (
        <EmptyState message={t("notification.empty")} />
      ) : (
        <div className="space-y-2">
          {data.results.map((n) => (
            <div key={n.id} className={`card p-4 flex items-center justify-between ${n.is_read ? "opacity-60" : ""}`}>
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <Badge color={n.type === "OVERDUE" ? "red" : n.type === "DUE_SOON" ? "yellow" : "blue"}>
                    {n.type.replace("_", " ")}
                  </Badge>
                  {!n.is_read && <span className="w-2 h-2 rounded-full bg-brand-600" />}
                </div>
                <p className="text-sm">{n.message}</p>
                <p className="text-xs text-slate-400 mt-1">{new Date(n.created_at).toLocaleString()}</p>
              </div>
              {!n.is_read && (
                <button onClick={() => markRead.mutate(n.id)} className="btn-secondary text-xs">
                  {t("notification.markRead")}
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
