import { useTranslation } from "react-i18next";
import { Spinner } from "./Spinner";

export function EmptyState({ message }) {
  const { t } = useTranslation();
  return (
    <div className="text-center py-12 text-slate-400">
      <p>{message || t("common.empty")}</p>
    </div>
  );
}

export function LoadingState() {
  const { t } = useTranslation();
  return (
    <div className="flex items-center justify-center gap-2 py-12 text-slate-500">
      <Spinner />
      <span>{t("common.loading")}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  const { t } = useTranslation();
  return (
    <div className="text-center py-12 text-red-600">
      <p className="mb-2">{message || t("common.error")}</p>
      {onRetry && (
        <button onClick={onRetry} className="btn-secondary">
          {t("common.retry")}
        </button>
      )}
    </div>
  );
}
