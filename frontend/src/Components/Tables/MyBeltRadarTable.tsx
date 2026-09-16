// React
import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMySessions } from '@/Api/BeltRadar';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { Session } from '@/Components/Props/BeltRadarProps';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import BaseTable from '@/Components/Tables/BaseTable';
import { getSessionColumns } from '@/Components/Tables/TableColumns';

function MyBeltRadarTable() {
	const { t } = useTranslation();
	const { characterID } = useParams();
	const [session, setSession] = useState<Session | Record<string, never>>({});
	const [modalAction, setModalAction] = useState<string | null>(null);

	// Load My Belt Radar sessions data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: queryKeys.mySessions(Number(characterID)),
		queryFn: () => loadMySessions(Number(characterID)),
		refetchOnWindowFocus: false,
		enabled: !!characterID,
	});

	// Define table columns for the my belt radar sessions
	const columns = useMemo(
		() => getSessionColumns(t, setSession, setModalAction),
		[t],
	);

	return (
		<>
			<BaseTable
				data={sessionData ?? []}
				isError={isErrorSessions}
				isFetching={isFetchingSessions}
				columns={columns}
			/>
			<BeltRadarModals
				session={session as Session}
				modalAction={modalAction}
				setModalAction={setModalAction}
				t={t}
				queryKey={queryKeys.mySessions(Number(characterID))}
			/>
		</>
	);
}

export default MyBeltRadarTable;
