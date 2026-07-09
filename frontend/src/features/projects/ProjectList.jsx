import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useProjects } from "./hooks/useProjects";
import { ProjectForm } from "./ProjectForm";
import { Modal } from "../../components/ui/Modal";
import { Badge } from "../../components/ui/Badge";
import { EmptyState, ErrorState, LoadingState } from "../../components/ui/states";

const STATUS_COLOR = {
  Planning: "slate",
  Active: "green",
  OnHold: "yellow",
  Completed: "blue",
  Archived: "slate",
};

export default function ProjectList() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const { data, isLoading, isError, refetch } = useProjects();

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("nav.projects")}</h1>
        <button onClick={() => setOpen(true)} className="btn-primary">{t("project.new")}</button>
      </div>

      {isLoading && <LoadingState />}
      {isError && <ErrorState onRetry={refetch} />}
      {data && (
        data.results.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.results.map((p) => (
              <Link key={p.id} to={`/projects/${p.id}`} className="card p-5 hover:shadow-md transition">
                <div className="flex items-start justify-between gap-2 mb-2">
                  <h2 className="font-semibold text-lg">{p.title}</h2>
                  <Badge color={STATUS_COLOR[p.status] || "slate"}>{p.status}</Badge>
                </div>
                <p className="text-sm text-slate-500 line-clamp-2 mb-3">{p.description || "—"}</p>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-3 text-slate-500">
                    <span>{p.tasks_count} {t("project.tasksCount")}</span>
                    <span>{p.members_count} {t("project.membersCount")}</span>
                  </div>
                  <span className="font-semibold text-brand-700">{p.progress}%</span>
                </div>
                <div className="mt-3 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full bg-brand-600" style={{ width: `${p.progress}%` }} />
                </div>
              </Link>
            ))}
          </div>
        )
      )}

      <Modal open={open} onClose={() => setOpen(false)} title={t("project.new")}>
        <ProjectForm onDone={() => setOpen(false)} />
      </Modal>
    </div>
  );
}
