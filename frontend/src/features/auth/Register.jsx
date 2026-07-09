import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../lib/api";
import { useToast } from "../../contexts/ToastContext";

const schema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(8),
  first_name: z.string().optional(),
  last_name: z.string().optional(),
});

export default function Register() {
  const { t } = useTranslation();
  const toast = useToast();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ resolver: zodResolver(schema) });

  async function onSubmit(values) {
    try {
      await api.post("/auth/register/", values);
      toast.success(t("auth.registerSuccess"));
      navigate("/login");
    } catch (err) {
      const msg = err.response?.data?.username?.[0] || err.response?.data?.email?.[0] || t("common.error");
      toast.error(msg);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="card w-full max-w-sm p-8">
        <h1 className="text-2xl font-bold text-brand-700 mb-6">{t("auth.register")}</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="label" htmlFor="reg-username">{t("auth.username")}</label>
            <input id="reg-username" className="input" {...register("username")} aria-invalid={!!errors.username} />
            {errors.username && <p className="error-text">{errors.username.message}</p>}
          </div>
          <div>
            <label className="label" htmlFor="reg-email">{t("auth.email")}</label>
            <input id="reg-email" className="input" type="email" {...register("email")} aria-invalid={!!errors.email} />
            {errors.email && <p className="error-text">{errors.email.message}</p>}
          </div>
          <div>
            <label className="label" htmlFor="reg-password">{t("auth.password")}</label>
            <input id="reg-password" type="password" className="input" {...register("password")} aria-invalid={!!errors.password} />
            {errors.password && <p className="error-text">{t("auth.passwordMin")}</p>}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">{t("auth.firstName")}</label>
              <input className="input" {...register("first_name")} />
            </div>
            <div>
              <label className="label">{t("auth.lastName")}</label>
              <input className="input" {...register("last_name")} />
            </div>
          </div>
          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? t("common.loading") : t("auth.registerSubmit")}
          </button>
        </form>
        <p className="text-sm text-center mt-4 text-slate-500">
          <Link to="/login" className="text-brand-600 hover:underline">{t("auth.haveAccount")}</Link>
        </p>
      </div>
    </div>
  );
}
