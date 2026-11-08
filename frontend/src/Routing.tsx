// React
import React from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AaReactProvider, AuthBase, ErrorPage } from "aa-geuthur-react";
import { NuqsAdapter } from "nuqs/adapters/react-router/v8";

// AA Belt Radar
import { AppName, ProjectName } from "@/constants";
import BeltRadar from "@/Pages/BeltRadar";
import MyBeltRadar from "@/Pages/MyBeltRadar";
import BeltRadarSession from "@/Pages/Session";
import SettingsPage from "@/Pages/SettingsPage";

const queryClient = new QueryClient();

function Routing() {
  return (
    <React.StrictMode>
      <AaReactProvider projectName={ProjectName} appName={AppName}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            <NuqsAdapter>
              <Routes>
                <Route path={`/${ProjectName}/`} element={<AuthBase fluidOnSmallScreens />}>
                  <Route index element={<BeltRadar />} />
                  <Route path=":characterID/" element={<BeltRadar />} />
                  <Route path="my-belt-radar/" element={<MyBeltRadar />} />
                  <Route path="my-belt-radar/:characterID/" element={<MyBeltRadar />} />
                  <Route path="settings/" element={<SettingsPage />} />
                  <Route path="session/:publicID/" element={<BeltRadarSession />} />
                  <Route path="*" element={<ErrorPage />} />
                </Route>
                <Route path="*" element={<Navigate to={`/${ProjectName}/`} replace />} />
              </Routes>
            </NuqsAdapter>
          </BrowserRouter>
        </QueryClientProvider>
      </AaReactProvider>
    </React.StrictMode>
  );
}

export default Routing;
