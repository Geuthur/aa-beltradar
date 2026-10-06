// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import { formatEta, formatNumber } from '@/Components/Base/BaseTable/tableHelper';

export function SessionBeltStats({ sessionData }: { sessionData?: SessionStats}) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tBeltSize = t("Belt Size");
    const tSpeed = t("Speed");
    const tETA = t("ETA");
    const tDone = t("Done");

    const finishEta = formatEta(sessionData?.stats?.finish_eta, tDone);

    return (
        <div className="br-stat-row">
            <div>
                <span className="br-stat-label">{tBeltSize}</span>
                <span className="br-stat-value">{formatNumber(Number(sessionData?.stats?.belt_volume_left_m3 ?? 0))} / {formatNumber(Number(sessionData?.stats?.belt_volume ?? 0))} m³</span>
            </div>
            <div>
                <span className="br-stat-label">{tSpeed}</span>
                <span className="br-stat-value">{formatNumber(Number(sessionData?.stats?.mining_rate_m3_per_s ?? 0))} m³/s</span>
            </div>
            <div>
                <span className="br-stat-label">{tETA}</span>
                <span className="br-stat-value">{finishEta}</span>
            </div>
        </div>
    );
}
