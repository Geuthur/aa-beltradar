// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import { renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';
export function SessionBeltExpectation({ sessionData }: { sessionData?: SessionStats}) {
    const { t } = useTranslation();
    return (
        <div className="row text-muted small mt-2">
            <div className="col-4 text-start">
                <strong>{t("Belt Type")}: </strong>
                <span>
                    {
                        renderTooltip(
                            t('The expected type of the asteroid belt.'),
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span><br />
                <span>{sessionData?.stats?.expected_belt_type ?? "N/A"}</span>
            </div>
            <div className="col-4 text-center">
                <strong>{t("Belt Size")}: </strong>
                <span>
                    {
                        renderTooltip(
                            t('The expected size of the asteroid belt.'),
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span><br />
                <span>{sessionData?.stats?.expected_belt_size ?? "N/A"}</span>
            </div>
            <div className="col-4 text-end">
                <strong>{t("Total Snapshots")}: </strong><br />
                <span>{sessionData?.total_timestamps ?? "N/A"}</span>
                {Boolean(sessionData?.has_timer || sessionData?.actions?.delete) && (
                    <span className="ms-2 text-primary" title={t("Belt Timer active")}>
                        <i className="fa-solid fa-stopwatch"></i>
                    </span>
                )}
            </div>
        </div>
    );
}
