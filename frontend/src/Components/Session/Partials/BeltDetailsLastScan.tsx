// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { Session } from "@/Api/schema";
import { formatDate, renderTooltip } from '@/Components/Helpers/functions';
import Styles from '@/Components/Session/Partials/BeltDetails.module.css';
export function BeltDetailsLastScan({ sessionData }: { sessionData: Session}) {
    const { t } = useTranslation();
    const options: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" };
    const progressPercent = Math.min(Math.max(sessionData?.stats?.progress_percent || 0, 0), 100);

    // Do not render the component if progress is 0 or less
    if (progressPercent <= 0) {
        return null;
    }

    return (
        <div className={`${Styles['last-scan-container']}`} style={{ width: `${progressPercent}%` }}>
            <small className={`${Styles['last-scan']} me-2`}>
                {
                    renderTooltip(
                        `${t("Last Scan")}: ${formatDate(sessionData?.last_timestamp, options)}`,
                        <span>{formatDate(sessionData?.last_timestamp, options)}</span>
                    )
                }
            </small>
        </div>
    );
}
