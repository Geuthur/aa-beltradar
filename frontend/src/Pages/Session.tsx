// React
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadSession } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import ErrorLoader from '@/Components/Loader/ErrorLoader';
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import SessionDashboard from '@/Components/Session/Dashboard';
import SessionSnapshotTable from '@/Components/Session/SnapshotTable';

function BeltRadarSession() {
    const { t } = useTranslation();
    const { publicID } = useParams();

	// Load Belt Radar Session Snapshot data
	const { data: sessionData, isError: isErrorSessions } = useQuery({
		queryKey: queryKeys.Session(String(publicID)),
        queryFn: () => loadSession(String(publicID)),
		refetchOnWindowFocus: false,
		enabled: !!publicID,
	});

    if (isErrorSessions) {
        return <ErrorLoader title={t("Error 400")} message={t("Error loading session data")} />;
    }

    const headerName = sessionData?.name ? `${t("Session")} - ${sessionData.name}` : t("Session");
    return (
        <main>
            {/* Sessions Section */}
            <BaseSectionHeader name={headerName} />
            {/* Session Dashboard */}
            <SessionDashboard sessionData={sessionData} />
            {/* Session Snapshot Table */}
            <SessionSnapshotTable />
        </main>
    )
}

export default BeltRadarSession
