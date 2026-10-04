// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from "@/Api/schema";
import { renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

export function SessionBeltExpectation({ sessionData }: { sessionData?: SessionStats}) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tBeltType = t("Belt Type");
    const tBeltSize = t("Belt Size");
    const tTotalSnapshots = t("Total Snapshots");
    const tBeltTimerActive = t("Belt Timer active");
    const tTooltipBeltType = t('The expected type of the asteroid belt.');
    const tTooltipBeltSize = t('The expected size of the asteroid belt.');

    return (
        <div className="br-stat-row">
            <div>
                <span className="br-stat-label">
                    {tBeltType}{' '}
                    {
                        renderTooltip(
                            tTooltipBeltType,
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span>
                <span className="br-stat-value">{sessionData?.stats?.expected_belt_type ?? "N/A"}</span>
            </div>
            <div>
                <span className="br-stat-label">
                    {tBeltSize}{' '}
                    {
                        renderTooltip(
                            tTooltipBeltSize,
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span>
                <span className="br-stat-value">{sessionData?.stats?.expected_belt_size ?? "N/A"}</span>
            </div>
            <div>
                <span className="br-stat-label">{tTotalSnapshots}</span>
                <span className="br-stat-value">{sessionData?.total_timestamps ?? "N/A"}</span>
                {Boolean(sessionData?.has_timer || sessionData?.actions?.delete) && (
                    renderTooltip(
                        tBeltTimerActive,
                        <span className="ms-2 br-timer-icon">
                            <i className="fa-solid fa-stopwatch"></i>
                        </span>
                    )
                )}
            </div>
        </div>
    );
}
