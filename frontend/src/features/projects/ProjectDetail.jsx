import { useTranslation } from "react-i18next";
import { Link, useParams } from "react-router-dom";
import { useProject } from "./hooks/useProjects";
import { Badge } from "../../components/ui/Badge";
import { ErrorState, LoadingState } from "../../components/ui/states";
import KanbanBoard from "../tasks/KanbanBoard";

export default function ProjectDetail() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { data: project, isLoading, isError, refetch } = useProject(id);

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div>
      <Link to="/projects" className="text-sm text-brand-600 hover:underline mb-2 inline-block">
        ← {t("common.back")}
      </Link>
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">{project.title}</h1>
          <p className="text-slate-500 mt-1">{project.description || "—"}</p>
        </div>
        <div className="flex items-center gap-3">
          <Badge color="green">{project.status}</Badge>
          <div className="text-end">
            <div className="text-2xl font-bold text-brand-700">{project.progress}%</div>
            <div className="text-xs text-slate-400">{t("project.progress")}</div>
          </div>
        </div>
      </div>

      <div className="mb-4 h-2 bg-slate-100 rounded-full overflow-hidden">
        <div className="h-full bg-brand-600" style={{ width: `${project.progress}%` }} />
      </div>

      <KanbanBoard projectId={project.id} />
    </div>
  );
}
