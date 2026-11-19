// React
import React from "react";

// Third Party
import { useUserSettings } from "aa-geuthur-react";
import { BellOff, Settings2 } from "lucide-react";
import { Card } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import type { components } from "@/Api/OpenApi";
import styles from "@/Styles/modules/SettingsPage.module.css";

type UserSettings = components["schemas"]["UserSettingsSchema"];
type UserSettingsUpdate = components["schemas"]["UserSettingsUpdateRequest"];

export const SettingsPage: React.FC = () => {
  const { t } = useTranslation();
  // Loads the settings and saves them optimistically (rollback on error)
  const { data, isLoading, isError, updateMutation } = useUserSettings<UserSettings, UserSettingsUpdate>();

  if (isLoading) {
    return (
      <div className="aa-loader-container">
        <span className="spinner-border" />
        <span>{t("Loading settings...")}</span>
      </div>
    );
  }

  if (isError || !data) {
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
              checked={data.disable_notifications}
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
