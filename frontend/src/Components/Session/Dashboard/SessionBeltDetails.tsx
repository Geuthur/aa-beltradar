// Third Party
import { ProgressBar } from 'react-bootstrap'
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionStats } from '@/Api/schema';
import { BeltDetailsFirstScan } from '@/Components/Session/Dashboard/BeltDetailsFirstScan';
import { BeltDetailsLastScan } from '@/Components/Session/Dashboard/BeltDetailsLastScan';
import Styles from '@/Components/Session/Dashboard/SessionBeltDetails.module.css';
import { BeltDetailsETA } from '@/Components/Session/Dashboard/SessionBeltDetailsETA';
import { formatNumber, renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

// Mirrors AUTO_TIMER_REMAINING_SHARE in beltradar/constants.py
const AUTO_TIMER_REMAINING_PERCENT = 10;

export function SessionBeltDetails({ sessionData }: { sessionData?: SessionStats }) {
    const { t } = useTranslation();
    const progressPercent = Math.min(Math.max(sessionData?.stats?.progress_percent || 0, 0), 100);
    const remainingPercent = 100 - progressPercent;
    const isAutoTimerReady = progressPercent > 0 && remainingPercent <= AUTO_TIMER_REMAINING_PERCENT;
    return (
        <div className="mt-3">
            <h3 className="br-asteroid-count">
                {sessionData?.stats?.remaining_asteroids || 0} / {sessionData?.stats?.total_asteroids || 0} <span id="session-progression"></span>
                <span>{t("asteroids")}</span>
                <span className="br-remaining-percent">({formatNumber(remainingPercent, undefined, { maximumFractionDigits: 1 })}% {t("left")})</span>
                {isAutoTimerReady && renderTooltip(
                    t("Auto Belt Timer ready"),
                    <span className="aa-status-dot br-timer-ready">
                        <span className="aa-status-ping" />
                        <span className="aa-status-dot-fill aa-status-dot-ready" />
                    </span>
                )}
            </h3>
            <div className="position-relative mt-2">
                <ProgressBar className={`br-progress ${Styles['belt-details']}`} striped={true} animated={true} now={progressPercent}/>
                <div className={Styles['belt-progress-container']}>
                    <BeltDetailsFirstScan sessionData={sessionData} />
                    <BeltDetailsLastScan sessionData={sessionData} />
                    <BeltDetailsETA sessionData={sessionData} />
                </div>
            </div>
        </div>
    );
}
