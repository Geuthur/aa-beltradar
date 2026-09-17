// React
import { useMemo } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMySessions } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import type { Session } from "@/Api/schema";
import { useModalQueryState } from '@/Components/Modals/BaseModal/useModalState';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import BaseTable from '@/Components/Tables/BaseTable';
import { getSessionColumns } from '@/Components/Tables/TableColumns';

function MyBeltRadarTable() {
	const { t } = useTranslation();
	const { characterID } = useParams();
	const { activeModal, activeEntityId, openModal, closeModal } = useModalQueryState();

	// Load My Belt Radar sessions data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: queryKeys.mySessions(Number(characterID)),
		queryFn: () => loadMySessions(Number(characterID)),
		refetchOnWindowFocus: false,
		enabled: !!characterID,
	});

	const activeSession = useMemo(
		() => sessionData?.find((s) => s.public_id === activeEntityId) ?? null,
		[sessionData, activeEntityId],
	);

	// Define table columns for the my belt radar sessions
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
				queryKey={queryKeys.mySessions(Number(characterID))}
			/>
		</>
	);
}

export default MyBeltRadarTable;
