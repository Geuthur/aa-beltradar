// Third Party
import moment from "moment";
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";

export function SessionBeltStats({ sessionData }: { sessionData?: SessionStats}) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tBeltSize = t("Belt Size");
    const tSpeed = t("Speed");
    const tETA = t("ETA");
    const tDone = t("Done");

    let finishEta;

    if (!sessionData?.stats?.finish_eta) {
        finishEta = "N/A"
    } else {
        if (moment(sessionData?.stats?.finish_eta).isAfter(moment())) {
            finishEta = moment(sessionData?.stats?.finish_eta).fromNow();
        } else {
            finishEta = tDone;
        }
    }

    return (
        <div className="row text-muted text-center mt-2">
            <div className="col-4 text-start">
                <strong>{tBeltSize}: </strong><br />
                <span>{sessionData?.stats?.belt_volume_left_m3 || '0'} / {sessionData?.stats?.belt_volume || '0'} m³</span>

            </div>
            <div className="col-4 text-center">
                <strong>{tSpeed}: </strong><br />
                <span>{sessionData?.stats?.mining_rate_m3_per_s ?? 0} m³/s</span>
            </div>
            <div className="col-4 text-end">
                <strong>{tETA}: </strong><br />
                <span>{finishEta}</span>
            </div>
        </div>
    );
}
