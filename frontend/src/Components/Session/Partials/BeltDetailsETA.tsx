// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { Session } from "@/Api/schema";
import { formatDate, renderTooltip } from '@/Components/Helpers/functions';
import Styles from '@/Components/Session/Partials/BeltDetails.module.css';
export function BeltDetailsETA({ sessionData }: { sessionData?: Session }) {
    const { t } = useTranslation();
    const options: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" };
    const progressPercent = Math.min(Math.max(sessionData?.stats?.progress_percent || 0, 0), 100);

    // Hide ETA if progress is 80% or more
    if (progressPercent >= 80) {
        return null;
    }

    return (
        <small className={`${Styles['belt-eta']} ps-3 pe-2`}>
            {
                renderTooltip(
                    `${t("Finish ETA")}: ${formatDate(sessionData?.stats?.finish_eta, options)}`,
                    <span>{formatDate(sessionData?.stats?.finish_eta, options)}</span>
                )
            }
        </small>
    );
}
