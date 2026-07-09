import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQueryClient } from "@tanstack/react-query";

import { Modal } from "../../components/ui/Modal";
import { Badge } from "../../components/ui/Badge";
import { useSetProgress, useTransitionTask, useTaskComments, useAddComment } from "./hooks/useTasks";
import { useToast } from "../../contexts/ToastContext";
import api from "../../lib/api";

const STATUSES = ["Todo", "InProgress", "Review", "Done"];
const PRIORITY_COLOR = { Low: "slate", Medium: "blue", High: "yellow", Urgent: "red" };

export default function TaskDetail({ task, projectId, onClose }) {
  const { t } = useTranslation();
  const toast = useToast();
  const qc = useQueryClient();
  const setProgress = useSetProgress(projectId);
  const transition = useTransitionTask(projectId);
  const { data: comments, isLoading } = useTaskComments(task.id);
  const addComment = useAddComment(task.id);
  const [body, setBody] = useState("");

  function handleProgress(value) {
    setProgress.mutate(
      { id: task.id, value },
      { onError: () => toast.error(t("common.error")) }
    );
  }

  function handleStatus(status) {
    transition.mutate(
      { id: task.id, status },
      {
        onError: (err) => {
          const msg = err.response?.data?.detail || t("task.illegalTransition");
          toast.error(msg);
        },
      }
    );
  }

  function handleComment(e) {
    e.preventDefault();
    if (!body.trim()) return;
    addComment.mutate(body, {
      onSuccess: () => setBody(""),
      onError: () => toast.error(t("common.error")),
    });
  }

  async function handleFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      await api.post(`/tasks/${task.id}/attachments/`, (() => {
        const f = new FormData(); f.append("file", file); return f;
      })(), { headers: { "Content-Type": "multipart/form-data" } });
      toast.success(t("common.save"));
      qc.invalidateQueries({ queryKey: ["task", task.id, "attachments"] });
    } catch {
      toast.error(t("common.error"));
    }
  }

  return (
    <Modal open onClose={onClose} title={task.title}>
      <div className="space-y-5">
        <div className="flex items-center gap-2">
          <Badge color={PRIORITY_COLOR[task.priority]}>{t(`priority.${task.priority}`)}</Badge>
          {task.due_date && <span className="text-xs text-slate-500">📅 {task.due_date}</span>}
        </div>

        {task.description && <p className="text-sm text-slate-600">{task.description}</p>}

        <div>
          <label className="label">{t("task.status")}</label>
          <div className="flex flex-wrap gap-2">
            {STATUSES.map((s) => (
              <button
                key={s}
                onClick={() => handleStatus(s)}
                className={`px-3 py-1 rounded-lg text-sm ${
                  task.status === s ? "bg-brand-600 text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {t(`status.${s}`)}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="label">{t("task.progress")}: {task.progress}%</label>
          <input
            type="range"
            min={0}
            max={100}
            defaultValue={task.progress}
            onMouseUp={(e) => handleProgress(Number(e.target.value))}
            onKeyUp={(e) => handleProgress(Number(e.target.value))}
            className="w-full accent-brand-600"
          />
        </div>

        <div>
          <label className="label">{t("task.comments")}</label>
          {isLoading ? (
            <p className="text-xs text-slate-400">{t("common.loading")}</p>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {(comments || []).length === 0 && <p className="text-xs text-slate-400">{t("common.empty")}</p>}
              {(comments || []).map((c) => (
                <div key={c.id} className="bg-slate-50 rounded-lg p-2 text-sm">
                  <div className="text-xs text-slate-500 mb-1">{c.author} · {new Date(c.created_at).toLocaleDateString()}</div>
                  <p>{c.body}</p>
                </div>
              ))}
            </div>
          )}
          <form onSubmit={handleComment} className="mt-2 flex gap-2">
            <input
              className="input"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              placeholder={t("task.addComment")}
            />
            <button type="submit" className="btn-primary shrink-0" disabled={addComment.isPending || !body.trim()}>
              {t("common.save")}
            </button>
          </form>
        </div>

        <div>
          <label className="label">📎 {t("task.comments")}</label>
          <input type="file" onChange={handleFile} className="text-sm" />
        </div>
      </div>
    </Modal>
  );
}
