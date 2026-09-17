// React
import { useState } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadSession } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import ErrorLoader from '@/Components/Loader/ErrorLoader';
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import SessionCharts from '@/Components/Session/Charts';
import SessionDashboard from '@/Components/Session/Dashboard';
import SessionHeaderButtons from '@/Components/Session/Header';
import SessionModals from '@/Components/Session/Modals';
import SessionSnapshotTable from '@/Components/Session/SnapshotTable';

function BeltRadarSession() {
    const { t } = useTranslation();
    const { publicID } = useParams();
    const [activeModal, setActiveModal] = useState<string | null>(null);

    const sessionKey = queryKeys.Session(String(publicID));

    // Load Belt Radar Session Snapshot data
    const { data: sessionData, isError: isErrorSessions } = useQuery({
        queryKey: sessionKey,
        queryFn: () => loadSession(String(publicID)),
        refetchOnWindowFocus: false,
        enabled: !!publicID,
    });

    if (isErrorSessions) {
        return <ErrorLoader title={t("Error 400")} message={t("Error loading session data")} />;
    }

    const headerName = sessionData?.name ? `${t("Session")} - ${sessionData.name}` : t("Session");
    const hasTimer = Boolean(sessionData?.has_timer || sessionData?.actions?.delete);

    return (
        <main>
            {/* Sessions Section */}
            <BaseSectionHeader name={headerName}>
                <SessionHeaderButtons
                    hasTimer={hasTimer}
                    deleteTimerAction={sessionData?.actions?.delete}
                    createTimerAction={sessionData?.actions?.create}
                    onAction={setActiveModal}
                />
            </BaseSectionHeader>
            {/* Session Dashboard */}
            <SessionDashboard sessionData={sessionData} />
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
        </main>
    );
}

export default BeltRadarSession;
