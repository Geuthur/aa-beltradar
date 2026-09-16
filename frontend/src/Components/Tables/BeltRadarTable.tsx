// React
import { useMemo } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadPublicSessions } from '@/Api/BeltRadar';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { Session } from "@/Api/schema";
import { queryKeys } from "@/Api/query";
import BaseTable from '@/Components/Tables/BaseTable';
import { getSessionColumns } from '@/Components/Tables/TableColumns';
import { useModalQueryState } from '@/Hooks/useModalState';

function BeltRadarTable() {
	const { t } = useTranslation();
	const { activeModal, activeEntityId, openModal, closeModal } = useModalQueryState();

	// Load Belt Radar public sessions data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: queryKeys.publicSessions,
		queryFn: () => loadPublicSessions(),
		refetchOnWindowFocus: false,
	});

	const activeSession = useMemo(
		() => sessionData?.find((s) => s.public_id === activeEntityId) ?? null,
		[sessionData, activeEntityId],
	);

	// Define table columns for public sessions
	const columns = useMemo(
		() =>
			getSessionColumns(
				t,
				(session: Session) => session,
				(actionId: string | null, row?: Session) => {
					if (actionId && row) {
						openModal(actionId, row.public_id);
					} else {
						closeModal();
					}
				},
			),
		[t, openModal, closeModal],
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
				session={activeSession}
				modalAction={activeModal}
				setModalAction={(action) => (!action ? closeModal() : openModal(action))}
				t={t}
				queryKey={queryKeys.publicSessions}
			/>
		</>
	);
}

export default BeltRadarTable;
