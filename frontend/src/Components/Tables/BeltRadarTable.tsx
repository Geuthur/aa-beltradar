// React
import { useMemo, useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadPublicSessions } from '@/Api/BeltRadar';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { Session } from '@/Components/Props/BeltRadarProps';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import BaseTable from '@/Components/Tables/BaseTable';
import { getSessionColumns } from '@/Components/Tables/TableColumns';

function BeltRadarTable() {
	const { t } = useTranslation();
	const [session, setSession] = useState<Session | Record<string, never>>({});
	const [modalAction, setModalAction] = useState<string | null>(null);

	// Load Belt Radar public sessions data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: queryKeys.publicSessions,
		queryFn: () => loadPublicSessions(),
		refetchOnWindowFocus: false,
	});

	// Define table columns for public sessions
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
				queryKey={queryKeys.publicSessions}
			/>
		</>
	);
}

export default BeltRadarTable;
