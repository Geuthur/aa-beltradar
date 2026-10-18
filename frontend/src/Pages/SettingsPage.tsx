// React
import React from "react";

// Third Party
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { BellOff, Settings2 } from "lucide-react";
import { Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { loadUserData, updateUserSettings } from "@/Api/ApiCalls";
import type { components } from "@/Api/OpenApi";
import { queryKeys } from "@/Api/query";
import styles from "@/Styles/modules/SettingsPage.module.css";

type UserDataResponse = { user: components["schemas"]["UserData"] };

export const SettingsPage: React.FC = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: queryKeys.User,
    queryFn: loadUserData,
  });

  const updateMutation = useMutation({
    mutationFn: (settings: { disable_notifications: boolean }) => updateUserSettings(settings),
    onMutate: async (settings) => {
      await queryClient.cancelQueries({ queryKey: queryKeys.User });
      const previous = queryClient.getQueryData<UserDataResponse>(queryKeys.User);
      if (previous) {
        queryClient.setQueryData<UserDataResponse>(queryKeys.User, {
          ...previous,
          user: {
            ...previous.user,
            notification: settings.disable_notifications,
          },
        });
      }
      return { previous };
    },
    onError: (_error, _settings, context) => {
      if (context?.previous) {
        queryClient.setQueryData(queryKeys.User, context.previous);
      }
    },
    onSuccess: (_data, settings) => {
      queryClient.setQueryData<UserDataResponse>(queryKeys.User, (old) =>
        old
          ? {
              ...old,
              user: {
                ...old.user,
                notification: settings.disable_notifications,
              },
            }
          : old,
      );
    },
  });

  if (isLoading) {
    return (
      <div className="aa-loader-container">
        <span className="spinner-border" />
        <span>{t("Loading settings...")}</span>
      </div>
    );
  }

  if (isError || !data?.user) {
    return (
      <Card className="bg-secondary text-light border-0 shadow-sm" role="alert">
        <Card.Body className={styles["error"]}>
          {t("Failed to load settings. Please try refreshing the page.")}
        </Card.Body>
      </Card>
    );
  }

  return (
    <Card className={`${styles["page"]} border-0`}>
      <Card.Body className="bg-dark">
        <Card.Header className={styles["header"] + " bg-secondary"}>
          <Settings2 size={24} aria-hidden="true" />
          <div>
            <h1 className={styles["title"]}>{t("Settings")}</h1>
            <p className={styles["description"]}>{t("Manage your Belt Radar preferences.")}</p>
          </div>
        </Card.Header>

        <Card className="bg-secondary text-light border-0 shadow-sm">
          <Card.Body className={styles["setting-row"]}>
            <div className={styles["setting-copy"]}>
              <div className={styles["setting-title"]}>
                <BellOff size={18} aria-hidden="true" />
                <label htmlFor="disable-notifications">{t("Disable all notifications")}</label>
              </div>
              <p className={styles["setting-description"]}>
                {t("When enabled, Belt Radar will not send notifications to your Alliance Auth or Discord account.")}
              </p>
              {updateMutation.isError && (
                <p className={styles["error-message"]} role="alert">
                  {t("Could not save this setting. Your previous preference was restored.")}
                </p>
              )}
              {updateMutation.isPending && (
                <p className={styles["save-status"]} role="status">{t("Saving...")}</p>
              )}
            </div>
            <input
              id="disable-notifications"
              className={styles["switch"]}
              type="checkbox"
              role="switch"
              checked={data.user.notification}
              disabled={updateMutation.isPending}
              onChange={(event) =>
                updateMutation.mutate({ disable_notifications: event.currentTarget.checked })
              }
            />
          </Card.Body>
        </Card>
      </Card.Body>
    </Card>
  );
};

export default SettingsPage;
