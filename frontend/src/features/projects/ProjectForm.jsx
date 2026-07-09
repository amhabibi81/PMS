import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate } from "react-router-dom";
import { useCreateProject } from "./hooks/useProjects";
import { useToast } from "../../contexts/ToastContext";

const schema = z.object({
  title: z.string().min(1),
  description: z.string().optional(),
  start_date: z.string().min(1),
  due_date: z.string().optional(),
  status: z.enum(["Planning", "Active", "OnHold", "Completed", "Archived"]).default("Active"),
});

const STATUSES = ["Planning", "Active", "OnHold", "Completed", "Archived"];

export function ProjectForm({ initial, onDone }) {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();
  const create = useCreateProject();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: initial || { status: "Active", start_date: new Date().toISOString().slice(0, 10) },
  });

  async function onSubmit(values) {
    try {
      const p = await create.mutateAsync(values);
      toast.success(t("common.save"));
      onDone ? onDone(p) : navigate(`/projects/${p.id}`);
    } catch {
      toast.error(t("common.error"));
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="label" htmlFor="proj-title">{t("project.title")}</label>
        <input id="proj-title" className="input" {...register("title")} aria-invalid={!!errors.title} />
        {errors.title && <p className="error-text">{errors.title.message}</p>}
      </div>
      <div>
        <label className="label">{t("project.description")}</label>
        <textarea className="input" rows={3} {...register("description")} />
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label">{t("project.startDate")}</label>
          <input type="date" className="input" {...register("start_date")} />
        </div>
        <div>
          <label className="label">{t("project.dueDate")}</label>
          <input type="date" className="input" {...register("due_date")} />
        </div>
      </div>
      <div>
        <label className="label">{t("project.status")}</label>
        <select className="input" {...register("status")}>
          {STATUSES.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
      </div>
      <button type="submit" className="btn-primary" disabled={isSubmitting}>
        {isSubmitting ? t("common.loading") : t("common.create")}
      </button>
    </form>
  );
}
