// Third Party
import moment from "moment";
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { Session } from '@/Components/Props/BeltRadarProps';
export function SessionBeltStats({ sessionData }: { sessionData: Session}) {
    const { t } = useTranslation();
    let finishEta;

    if (!sessionData?.stats?.finish_eta) {
        finishEta = "N/A"
    } else {
        if (moment(sessionData?.stats?.finish_eta).isAfter(moment())) {
            finishEta = moment(sessionData?.stats?.finish_eta).fromNow();
        } else {
            finishEta = t("Done");
        }
    }

    return (
        <div className="row text-muted text-center mt-2">
            <div className="col-4 text-start">
                <strong>{t("Belt Size")}: </strong><br />
                <span>{sessionData?.stats?.belt_volume_left_m3 || '0'} / {sessionData?.stats?.belt_volume || '0'} m³</span>

            </div>
            <div className="col-4 text-center">
                <strong>{t("Speed")}: </strong><br />
                <span>{sessionData?.stats?.mining_rate_m3_per_s} m³/s</span>
            </div>
            <div className="col-4 text-end">
                <strong>{t("ETA")}: </strong><br />
                <span>{finishEta}</span>
            </div>
        </div>
    );
}
