import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../contexts/AuthContext";
import { useToast } from "../../contexts/ToastContext";

const schema = z.object({
  username: z.string().min(1),
  password: z.string().min(1),
});

export default function Login() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) });

  async function onSubmit(values) {
    try {
      await login(values.username, values.password);
      navigate("/projects");
    } catch {
      toast.error(t("auth.loginFailed"));
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-sm p-8">
        <h1 className="text-2xl font-bold text-brand-700 mb-1">{t("auth.login")}</h1>
        <p className="text-sm text-slate-500 mb-6">{t("app.tagline")}</p>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label" htmlFor="login-username">{t("auth.username")}</label>
            <input id="login-username" className="input" {...register("username")} aria-invalid={!!errors.username} />
            {errors.username && <p className="error-text">{errors.username.message}</p>}
          </div>
          <div>
            <label className="label" htmlFor="login-password">{t("auth.password")}</label>
            <input id="login-password" type="password" className="input" {...register("password")} aria-invalid={!!errors.password} />
            {errors.password && <p className="error-text">{errors.password.message}</p>}
          </div>
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? t("common.loading") : t("auth.loginSubmit")}
          </button>
        </form>
        <p className="text-sm text-center mt-4 text-slate-500">
          <Link to="/register" className="text-brand-600 hover:underline">{t("auth.noAccount")}</Link>
        </p>
      </div>
    </div>
  );
}
