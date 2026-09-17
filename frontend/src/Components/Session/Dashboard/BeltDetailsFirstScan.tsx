// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import Styles from '@/Components/Session/Dashboard/SessionBeltDetails.module.css';
import { formatDate, renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

export function BeltDetailsFirstScan({ sessionData }: { sessionData?: SessionStats }) {
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
