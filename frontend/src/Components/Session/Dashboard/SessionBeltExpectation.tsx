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
        <div className="row text-muted small mt-2">
            <div className="col-4 text-start">
                <strong>{tBeltType}: </strong>
                <span>
                    {
                        renderTooltip(
                            tTooltipBeltType,
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span><br />
                <span>{sessionData?.stats?.expected_belt_type ?? "N/A"}</span>
            </div>
            <div className="col-4 text-center">
                <strong>{tBeltSize}: </strong>
                <span>
                    {
                        renderTooltip(
                            tTooltipBeltSize,
                            <i className="fa-solid fa-circle-question"></i>
                        )
                    }
                </span><br />
                <span>{sessionData?.stats?.expected_belt_size ?? "N/A"}</span>
            </div>
            <div className="col-4 text-end">
                <strong>{tTotalSnapshots}: </strong><br />
                <span>{sessionData?.total_timestamps ?? "N/A"}</span>
                {Boolean(sessionData?.has_timer || sessionData?.actions?.delete) && (
                    renderTooltip(
                        tBeltTimerActive,
                        <span className="ms-2 text-primary">
                            <i className="fa-solid fa-stopwatch"></i>
                        </span>
                    )
                )}
            </div>
        </div>
    );
}
