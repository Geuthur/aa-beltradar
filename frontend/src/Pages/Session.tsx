// React
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadSession } from '@/Api/BeltRadar';
import ErrorLoader from '@/Components/Loader/ErrorLoader';
import FetchingLoader from '@/Components/Loader/FetchingLoader';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import BaseSectionHeader from '@/Components/Section/BaseSectionHeader';
import SessionDashboard from '@/Components/Session/Dashboard';
import SessionSnapshotTable from '@/Components/Session/SnapshotTable';

function BeltRadarSession() {
    const { t } = useTranslation();
    const { publicID } = useParams();

	// Load Belt Radar Session Snapshot data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: queryKeys.Session(String(publicID)),
        queryFn: () => loadSession(String(publicID)),
		refetchOnWindowFocus: false,
		enabled: !!publicID,
	});

    if (isErrorSessions) {
        return <ErrorLoader title={t("Error 400")} message={t("Error loading session data")} />;
    }

    if (isFetchingSessions) {
        return <FetchingLoader message={t("Loading session data...")} />;
    }

    if (!sessionData) {
        return null;
    }

    const headerName = `${t("Session")} - ${sessionData.name}`;
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
