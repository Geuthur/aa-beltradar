// Third Party
import { ProgressBar } from 'react-bootstrap'
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { Session } from '@/Components/Props/BeltRadarProps';
import Styles from '@/Components/Session/Partials/BeltDetails.module.css';
import { BeltDetailsETA } from '@/Components/Session/Partials/BeltDetailsETA';
import { BeltDetailsFirstScan } from '@/Components/Session/Partials/BeltDetailsFirstScan';
import { BeltDetailsLastScan } from '@/Components/Session/Partials/BeltDetailsLastScan';

export function SessionBeltDetails({ sessionData }: { sessionData: Session}) {
    const { t } = useTranslation();
    const progressPercent = Math.min(Math.max(sessionData?.stats?.progress_percent || 0, 0), 100);
    return (
        <div className="text-center mt-2">
            <h3>
                {sessionData?.stats?.remaining_asteroids || 0} / {sessionData?.stats?.total_asteroids || 0} <span id="session-progression"></span>
                <span>{t("asteroids")}</span>
            </h3>
            <div className="position-relative">
                <ProgressBar className={`${Styles['belt-details']}`} striped={true} animated={true} now={progressPercent}/>
                <div className={Styles['belt-progress-container']}>
                    <BeltDetailsFirstScan sessionData={sessionData} />
                    <BeltDetailsLastScan sessionData={sessionData} />
                    <BeltDetailsETA sessionData={sessionData} />
                </div>
            </div>
        </div>
    );
}
