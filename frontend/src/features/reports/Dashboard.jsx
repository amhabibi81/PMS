import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend,
  LineChart, Line,
} from "recharts";
import { Link } from "react-router-dom";

import { useProjects } from "../projects/hooks/useProjects";
import { reportsApi } from "./api";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui";
import { LoadingState, EmptyState } from "../../components/ui/states";

const COLORS = { Todo: "#94a3b8", InProgress: "#3b82f6", Review: "#f59e0b", Done: "#22c55e" };

function ProjectReport({ project }) {
  const { t } = useTranslation();
  const [days] = useState(30);

  const summary = useQuery({ queryKey: ["report", "summary", project.id], queryFn: () => reportsApi.summary(project.id) });
  const dist = useQuery({ queryKey: ["report", "dist", project.id], queryFn: () => reportsApi.statusDistribution(project.id) });
  const workload = useQuery({ queryKey: ["report", "workload", project.id], queryFn: () => reportsApi.workload(project.id) });
  const overdue = useQuery({ queryKey: ["report", "overdue", project.id], queryFn: () => reportsApi.overdue(project.id) });
  const progress = useQuery({ queryKey: ["report", "progress", project.id, days], queryFn: () => reportsApi.progressOverTime(project.id, days) });

  function exportFile(fmt, type) {
    const url = reportsApi.exportUrl(project.id, fmt, type);
    const token = localStorage.getItem("access");
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.blob())
      .then((blob) => {
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `report_${project.id}.${fmt}`;
        link.click();
        URL.revokeObjectURL(link.href);
      });
  }

  if (summary.isLoading) return <LoadingState />;

  const s = summary.data;
  const distData = (dist.data || []).map((d) => ({ name: t(`status.${d.status}`), value: d.count, key: d.status }));
  const workData = (workload.data || []).map((w) => ({ name: w.username, open: w.open_tasks, overdue: w.overdue_tasks }));
  const overdueData = overdue.data || [];
  const progressData = (progress.data || []).map((p) => ({ name: new Date(p.timestamp).toLocaleDateString(), progress: p.project_progress }));

  return (
    <Card className="p-5 mb-6">
      <div className="flex items-start justify-between mb-4">
        <Link to={`/projects/${project.id}`} className="font-semibold text-lg hover:text-brand-700">{project.title}</Link>
        <div className="flex items-center gap-2">
          <Badge color={s.at_risk ? "red" : "green"}>{s.at_risk ? t("report.atRisk") : t("report.onTrack")}</Badge>
          <span className="font-bold text-brand-700">{s.progress}%</span>
        </div>
      </div>

      <div className="grid sm:grid-cols-4 gap-3 text-sm mb-4">
        <div className="card p-3"><div className="text-slate-400">{t("project.tasks")}</div><div className="text-xl font-bold">{s.total_tasks}</div></div>
        <div className="card p-3"><div className="text-slate-400">Done</div><div className="text-xl font-bold text-green-600">{s.done_tasks}</div></div>
        <div className="card p-3"><div className="text-slate-400">{t("report.overdue")}</div><div className="text-xl font-bold text-red-600">{s.overdue_count}</div></div>
        <div className="card p-3 flex flex-col justify-center">
          <div className="flex gap-2">
            <button onClick={() => exportFile("csv", "summary")} className="btn-secondary text-xs">{t("report.exportCsv")}</button>
            <button onClick={() => exportFile("pdf", "")} className="btn-secondary text-xs">{t("report.exportPdf")}</button>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="card p-4">
          <h3 className="font-medium mb-2 text-sm">{t("report.statusDistribution")}</h3>
          {distData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={distData} dataKey="value" nameKey="name" outerRadius={70} label>
                  {distData.map((d) => <Cell key={d.key} fill={COLORS[d.key] || "#94a3b8"} />)}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : <EmptyState />}
        </div>

        <div className="card p-4">
          <h3 className="font-medium mb-2 text-sm">{t("report.workload")}</h3>
          {workData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={workData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="open" name={t("task.status")} fill="#3b82f6" />
                <Bar dataKey="overdue" name={t("report.overdue")} fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          ) : <EmptyState />}
        </div>

        <div className="card p-4 md:col-span-2">
          <h3 className="font-medium mb-2 text-sm">{t("report.progressOverTime")}</h3>
          {progressData.length ? (
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={progressData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="progress" stroke="#16a34a" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : <EmptyState />}
        </div>

        <div className="card p-4 md:col-span-2">
          <h3 className="font-medium mb-2 text-sm">{t("report.overdue")}</h3>
          {overdueData.length ? (
            <table className="w-full text-sm">
              <thead><tr className="text-start text-slate-400"><th className="py-1 text-start">{t("task.title")}</th><th className="text-start">{t("task.assignee")}</th><th className="text-start">{t("task.dueDate")}</th><th className="text-start">{t("report.daysLate")}</th></tr></thead>
              <tbody>
                {overdueData.map((o) => (
                  <tr key={o.task_id} className="border-t border-slate-100">
                    <td className="py-2">{o.title}</td>
                    <td>{o.assignee || "—"}</td>
                    <td>{o.due_date}</td>
                    <td><Badge color="red">{o.days_late}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : <EmptyState />}
        </div>
      </div>
    </Card>
  );
}

export default function Dashboard() {
  const { t } = useTranslation();
  const { data, isLoading } = useProjects();

  if (isLoading) return <LoadingState />;
  const projects = data?.results || [];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">{t("nav.dashboard")}</h1>
      {projects.length === 0 ? <EmptyState /> : projects.map((p) => <ProjectReport key={p.id} project={p} />)}
    </div>
  );
}
