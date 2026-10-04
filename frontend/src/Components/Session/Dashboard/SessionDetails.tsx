// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";

export function SessionDetails({ sessionData }: { sessionData?: SessionStats }) {
    const { t } = useTranslation();
    return (
    <div className="br-stat-row">
        <div>
            <span className="br-stat-label">{t("Session Name")}</span>
            <span className="br-stat-value">{sessionData?.name || "-"}</span>
        </div>
        <div>
            <span className="br-stat-label">{t("Created At")}</span>
            <span className="br-stat-value">{sessionData?.created_at || "-"}</span>
        </div>
        <div>
            <span className="br-stat-label">{t("Owner")}</span>
            <span className="br-stat-value">{sessionData?.owner?.character_name || "-"}</span>
        </div>
    </div>
    );
}
