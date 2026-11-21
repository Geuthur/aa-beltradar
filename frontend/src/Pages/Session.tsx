// React
import { useState } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { BaseSectionHeader, ErrorLoader, LiveStatusIndicator } from "aa-geuthur-react";
import { Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadSession, SESSION_REFETCH_INTERVAL_MS, sessionQueryKeys } from '@/Api/calls/session';
import SessionCharts from '@/Components/Session/Charts';
import SessionDashboard from '@/Components/Session/Dashboard';
import SessionHeaderButtons from '@/Components/Session/Header';
import SessionModals from '@/Components/Session/Modals';
import SessionSnapshotTable from '@/Components/Session/SnapshotTable';

function BeltRadarSession() {
    const { t } = useTranslation();
    const { publicID } = useParams();
    const [activeModal, setActiveModal] = useState<string | null>(null);

    const sessionKey = sessionQueryKeys.session(String(publicID));

    // Load Belt Radar Session Snapshot data
    const {
        data: sessionData,
        isError: isErrorSessions,
        isFetching: isFetchingSession,
        dataUpdatedAt,
    } = useQuery({
        queryKey: sessionKey,
        queryFn: () => loadSession(String(publicID)),
        refetchOnWindowFocus: false,
        refetchInterval: SESSION_REFETCH_INTERVAL_MS,
        enabled: !!publicID,
    });

    if (isErrorSessions) {
        return <ErrorLoader title={t("Error 400")} message={t("Error loading session data")} />;
    }

    const headerName = sessionData?.name ? `${t("Session")} - ${sessionData.name}` : t("Session");
    const hasTimer = Boolean(sessionData?.has_timer || sessionData?.actions?.delete);

    return (
        <div className="br-page">
            {/* Sessions Section */}
            <BaseSectionHeader name={headerName}>
                <LiveStatusIndicator
                    isFetching={isFetchingSession}
                    dataUpdatedAt={dataUpdatedAt}
                    showTimestamp
                />
                <SessionHeaderButtons
                    hasTimer={hasTimer}
                    deleteTimerAction={sessionData?.actions?.delete}
                    createTimerAction={sessionData?.actions?.create}
                    onAction={setActiveModal}
                />
            </BaseSectionHeader>
            {/* Session Dashboard */}
            <Card className="bg-secondary text-light border-0 shadow-sm mb-3" aria-labelledby="session-stats">
                <SessionDashboard sessionData={sessionData} />
            </Card>
            {/* Session Snapshot Table */}
            <SessionSnapshotTable />
            {/* Session Charts */}
            <SessionCharts />

            {/* Belt Timer Modals */}
            <SessionModals
                session={sessionData}
                activeModal={activeModal}
                setActiveModal={setActiveModal}
            />
        </div>
    );
}

export default BeltRadarSession;
