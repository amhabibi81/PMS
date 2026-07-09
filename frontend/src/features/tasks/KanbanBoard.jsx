import { useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
  useDraggable,
} from "@dnd-kit/core";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";

import { useProjectTasks, useTransitionTask } from "./hooks/useTasks";
import { TaskCard } from "./TaskCard";
import TaskDetail from "./TaskDetail";
import { EmptyState, ErrorState, LoadingState } from "../../components/ui/states";
import { useToast } from "../../contexts/ToastContext";

const COLUMNS = ["Todo", "InProgress", "Review", "Done"];

function Column({ status, tasks, onCardClick, children }) {
  const { t } = useTranslation();
  const { setNodeRef, isOver } = useDroppable({ id: status });
  return (
    <div
      ref={setNodeRef}
      className={`flex-1 min-w-[220px] rounded-xl bg-slate-100/70 p-3 ${isOver ? "ring-2 ring-brand-500" : ""}`}
    >
      <div className="flex items-center justify-between mb-3">
        <h2 className="font-semibold text-sm">{t(`status.${status}`)}</h2>
        <span className="text-xs text-slate-400">{tasks.length}</span>
      </div>
      <div className="space-y-2 min-h-[80px]">
        {tasks.map((task) => (
          <DraggableTask key={task.id} task={task} onCardClick={onCardClick} />
        ))}
        {tasks.length === 0 && <p className="text-xs text-slate-400 text-center py-4">{t("common.empty")}</p>}
      </div>
      {children}
    </div>
  );
}

function DraggableTask({ task, onCardClick }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `task-${task.id}`,
    data: { task },
  });
  const style = transform
    ? { transform: `translate3d(${transform.x}px, ${transform.y}px, 0)`, opacity: isDragging ? 0.4 : 1 }
    : undefined;
  return (
    <TaskCard
      task={task}
      onClick={() => !isDragging && onCardClick(task)}
      draggableProps={{ setNodeRef, style, attributes }}
      listeners={listeners}
    />
  );
}

export default function KanbanBoard({ projectId }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const [activeId, setActiveId] = useState(null);
  const [selected, setSelected] = useState(null);

  const { data, isLoading, isError, refetch } = useProjectTasks(projectId);
  const transition = useTransitionTask(projectId);

  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 5 } }));

  const tasks = data?.results || [];
  const byStatus = (s) => tasks.filter((tk) => tk.status === s);
  const activeTask = tasks.find((tk) => `task-${tk.id}` === activeId);

  function onDragStart(e) {
    setActiveId(e.active.id);
  }

  function onDragEnd(e) {
    setActiveId(null);
    const { active, over } = e;
    if (!over) return;
    const task = active.data.current.task;
    const newStatus = over.id;
    if (task.status === newStatus) return;

    // Optimistic: update the cache immediately.
    const queryKey = ["tasks", { project: projectId }];
    const previous = qc.getQueryData(queryKey);
    qc.setQueryData(queryKey, (old) => {
      if (!old) return old;
      return {
        ...old,
        results: old.results.map((tk) => (tk.id === task.id ? { ...tk, status: newStatus } : tk)),
      };
    });

    transition.mutate(
      { id: task.id, status: newStatus },
      {
        onError: (err) => {
          qc.setQueryData(queryKey, previous); // rollback
          const msg = err.response?.data?.detail || t("task.illegalTransition");
          toast.error(`${t("task.transitionFailed")}: ${msg}`);
        },
        onSuccess: () => toast.success(t(`status.${newStatus}`)),
      }
    );
  }

  if (isLoading) return <LoadingState />;
  if (isError) return <ErrorState onRetry={refetch} />;

  return (
    <div>
      <DndContext sensors={sensors} onDragStart={onDragStart} onDragEnd={onDragEnd}>
        <div className="flex gap-3 overflow-x-auto pb-2">
          {COLUMNS.map((s) => (
            <Column key={s} status={s} tasks={byStatus(s)} onCardClick={setSelected} />
          ))}
        </div>
        <DragOverlay>
          {activeTask ? <TaskCard task={activeTask} /> : null}
        </DragOverlay>
      </DndContext>
      {tasks.length === 0 && <EmptyState />}
      {selected && <TaskDetail task={selected} projectId={projectId} onClose={() => setSelected(null)} />}
    </div>
  );
}
