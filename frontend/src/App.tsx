// React
import React from "react"
import {  BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "i18next";
import Backend from "i18next-http-backend";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";
import { initReactI18next, useTranslation } from "react-i18next";

// AA Belt Radar
import ErrorLoader from "@/Components/Base/Loader/ErrorLoader"
import BeltRadarBase from "@/Pages/Base";
import BeltRadar from "@/Pages/BeltRadar";
import MyBeltRadar from "@/Pages/MyBeltRadar";
import BeltRadarSession from "@/Pages/Session";
import SettingsPage from "@/Pages/SettingsPage";

const queryClient = new QueryClient();
export const AppName = "aa-beltradar";
export const ProjectName = "beltradar";

// Read language directly from Django's LANGUAGE_CODE (set as lang="..." on root div)
const djangoLanguage = typeof document !== "undefined" ? document.getElementById(`${AppName}-root`)?.getAttribute("lang") ?? "en" : "en";

i18n
  .use(Backend)
  .use(initReactI18next)
  .init({
    lng: djangoLanguage,
    fallbackLng: "en",
    keySeparator: false,
    nsSeparator: false,
    interpolation: {
      escapeValue: false, // react already safes from xss => https://www.i18next.com/translation-function/interpolation#unescape
    },
    react: {
      useSuspense: false, //   <---- this will do the magic
    },
    backend: {
      loadPath: `/static/${ProjectName}/i18n/{{lng}}/{{ns}}.json`,
    },
  });

function App() {
  const { t } = useTranslation();
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <NuqsAdapter>
            <Routes>
              <Route path="/beltradar/" element={<BeltRadarBase />}>
                <Route index element={<BeltRadar />} />
                <Route path=":characterID/" element={<BeltRadar />} />
                <Route path="my-belt-radar/" element={<MyBeltRadar />} />
                <Route path="my-belt-radar/:characterID/" element={<MyBeltRadar />} />
                <Route path="settings/" element={<SettingsPage />} />
                <Route path="session/:publicID/" element={<BeltRadarSession />} />
                <Route path="*" element={<ErrorLoader title={t("Error 404")} message={t("The page you are looking for does not exist.")} />} />
              </Route>
              <Route path="*" element={<Navigate to="beltradar/" replace />} />
            </Routes>
          </NuqsAdapter>
        </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>
  )
}

export default App
