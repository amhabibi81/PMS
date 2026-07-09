import { useTranslation } from "react-i18next";
import { setLanguage } from "../i18n";

export function LanguageSwitcher() {
  const { i18n, t } = useTranslation();
  return (
    <div className="flex items-center gap-1">
      <button
        onClick={() => setLanguage("fa")}
        className={`px-2 py-1 rounded text-sm ${i18n.language === "fa" ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"}`}
      >
        فا
      </button>
      <button
        onClick={() => setLanguage("en")}
        className={`px-2 py-1 rounded text-sm ${i18n.language === "en" ? "bg-brand-600 text-white" : "text-slate-600 hover:bg-slate-100"}`}
      >
        EN
      </button>
    </div>
  );
}
