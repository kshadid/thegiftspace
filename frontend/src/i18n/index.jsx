import React, { createContext, useContext, useMemo, useState, useEffect } from "react";

const I18nCtx = createContext({ t: (k) => k, locale: "en", setLocale: () => {} });

// Minimal resource map; extend as we add locales
const RESOURCES = {
  en: {
    common: {
      backToHome: "Back to home",
      contribute: "Contribute",
      share: "Share",
      searchGifts: "Search gifts…",
      gifts: "Gifts",
    },
    landing: {
      headline: "A modern wedding cash registry",
      getStarted: "Get Started",
      sample: "Sample",
    },
    public: {
      raised: "Raised",
      goal: "Goal",
      highlighted: "Highlighted",
      copyLink: "Copy",
      editRegistry: "Edit registry →",
    },
    legal: {
      terms: "Terms & Conditions",
      privacy: "Privacy Policy",
    },
  },
};

export function I18nProvider({ children, defaultLocale = "en" }) {
  const [locale, setLocale] = useState(defaultLocale);

  useEffect(() => {
    const saved = localStorage.getItem("locale");
    if (saved && RESOURCES[saved]) setLocale(saved);
  }, []);

  const t = useMemo(() => {
    return (key, ns = undefined) => {
      const path = (ns ? `${ns}.${key}` : key).split(".");
      let cur = RESOURCES[locale] || RESOURCES.en;
      for (const p of path) {
        if (!cur) break;
        cur = cur[p];
      }
      return cur || key;
    };
  }, [locale]);

  const value = useMemo(() => ({ t, locale, setLocale: (l) => { if (RESOURCES[l]) { localStorage.setItem("locale", l); setLocale(l); } } }), [t, locale]);

  return <I18nCtx.Provider value={value}>{children}</I18nCtx.Provider>;
}

export function useI18n() {
  return useContext(I18nCtx);
}