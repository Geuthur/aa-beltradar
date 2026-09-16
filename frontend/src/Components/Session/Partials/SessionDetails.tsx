// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { Session } from '@/Components/Props/BeltRadarProps';

export function SessionDetails({ sessionData }: { sessionData: Session }) {
    const { t } = useTranslation();
    return (
    <div className="row text-muted small mt-2">
        <div className="col-4 text-start">
            <strong>{t("Session Name")}: </strong> {sessionData?.name || "-"}
        </div>
        <div className="col-4 text-center">
            <strong>{t("Created At")}: </strong> {sessionData?.created_at || "-"}
        </div>
        <div className="col-4 text-end">
            <strong>{t("Owner")}: </strong> {sessionData?.owner?.character_name || "-"}
        </div>
    </div>
    );
}
