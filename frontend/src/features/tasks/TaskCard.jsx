import { useTranslation } from "react-i18next";
import { Badge } from "../../components/ui/Badge";

const PRIORITY_COLOR = {
  Low: "slate",
  Medium: "blue",
  High: "yellow",
  Urgent: "red",
};

export function TaskCard({ task, onClick, draggableProps, listeners }) {
  const { t } = useTranslation();
  return (
    <div
      ref={draggableProps?.setNodeRef}
      style={draggableProps?.style}
      {...listeners}
      {...draggableProps?.attributes}
      onClick={onClick}
      className="card p-3 cursor-pointer hover:shadow-md transition grab"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-medium text-sm leading-snug">{task.title}</h3>
        <Badge color={PRIORITY_COLOR[task.priority] || "slate"}>{t(`priority.${task.priority}`)}</Badge>
      </div>
      {task.due_date && (
        <div className="mt-2 text-xs text-slate-500 flex items-center justify-between">
          <span>📅 {task.due_date}</span>
          {task.assignee && <span>👤 {typeof task.assignee === "object" ? task.assignee.username : task.assignee}</span>}
        </div>
      )}
      {task.progress > 0 && (
        <div className="mt-2">
          <div className="h-1.5 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-brand-600" style={{ width: `${task.progress}%` }} />
          </div>
        </div>
      )}
    </div>
  );
}
