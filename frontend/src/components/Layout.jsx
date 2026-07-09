import { useQuery } from "@tanstack/react-query";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../lib/api";
import { useAuth } from "../contexts/AuthContext";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { Badge } from "./ui/Badge";

export function Layout() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const { data } = useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: async () => (await api.get("/notifications/?unread=true")).data,
  });
  const unread = data?.results?.length || 0;

  const navItem = ({ isActive }) =>
    `px-3 py-2 rounded-lg text-sm font-medium ${
      isActive ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"
    }`;

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const linkBase =
    "flex items-center gap-2";

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link to="/projects" className="flex items-center gap-2">
            <span className="text-xl font-bold text-brand-700">{t("app.name")}</span>
            <span className="text-xs text-slate-400">{t("app.tagline")}</span>
          </Link>
          <nav className="flex items-center gap-1">
            <NavLink to="/dashboard" className={navItem}>{t("nav.dashboard")}</NavLink>
            <NavLink to="/projects" className={navItem}>{t("nav.projects")}</NavLink>
            <NavLink to="/notifications" className={`${navItem} ${linkBase}`}>
              {t("nav.notifications")}
              {unread > 0 && <Badge color="red">{unread}</Badge>}
            </NavLink>
            <LanguageSwitcher />
            <div className="mx-2 text-sm text-slate-500">{user?.username}</div>
            <button onClick={handleLogout} className="btn-secondary">
              {t("nav.logout")}
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
