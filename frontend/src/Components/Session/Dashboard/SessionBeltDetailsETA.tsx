// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import Styles from '@/Components/Session/Dashboard/SessionBeltDetails.module.css';
import { formatDate, renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

export function BeltDetailsETA({ sessionData }: { sessionData?: SessionStats }) {
    const { t } = useTranslation();
    const options: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" };
    const progressPercent = Math.min(Math.max(sessionData?.stats?.progress_percent || 0, 0), 100);

    // Translations for tooltips and titles
    const tFinishETA = t("Finish ETA");

    // Hide ETA if progress is 80% or more
    if (progressPercent >= 80) {
        return null;
    }

    return (
        <small className={`${Styles['belt-eta']} ps-3 pe-2`}>
            {
                renderTooltip(
                    `${tFinishETA}: ${formatDate(sessionData?.stats?.finish_eta, options)}`,
                    <span>{formatDate(sessionData?.stats?.finish_eta, options)}</span>
                )
            }
        </small>
    );
}
