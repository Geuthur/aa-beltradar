// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { formatDate, renderTooltip } from '@/Components/Helpers/functions';
import type { Session } from '@/Components/Props/BeltRadarProps';
import Styles from '@/Components/Session/Partials/BeltDetails.module.css';

export function BeltDetailsFirstScan({ sessionData }: { sessionData: Session}) {
    const { t } = useTranslation();
    const options: Intl.DateTimeFormatOptions = { hour: "2-digit", minute: "2-digit" };
    return (
        <small className={`${Styles['first-scan']} ps-3 pe-2`}>
            {
                renderTooltip(
                    `${t("First Scan")}: ${formatDate(sessionData?.first_timestamp, options)}`,
                    <span>{formatDate(sessionData?.first_timestamp, options)}</span>
                )
            }
        </small>
    );
}
