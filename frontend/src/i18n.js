import i18n from "i18next";
import { initReactI18next } from "react-i18next";

import fa from "./locales/fa.json";
import en from "./locales/en.json";

i18n.use(initReactI18next).init({
  resources: {
    fa: { translation: fa },
    en: { translation: en },
  },
  lng: localStorage.getItem("lang") || "fa",
  fallbackLng: "en",
  interpolation: { escapeValue: false },
});

export function applyDirection(lang) {
  const dir = lang === "fa" ? "rtl" : "ltr";
  document.documentElement.setAttribute("dir", dir);
  document.documentElement.setAttribute("lang", lang);
}

export function setLanguage(lang) {
  i18n.changeLanguage(lang);
  localStorage.setItem("lang", lang);
  applyDirection(lang);
}

applyDirection(i18n.language);

export default i18n;
