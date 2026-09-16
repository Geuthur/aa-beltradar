// React
import { useMemo } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMyBeltTimers } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import type { BeltTimer } from "@/Api/schema";
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import BaseTable from '@/Components/Tables/BaseTable';
import { getBeltTimerColumns } from '@/Components/Tables/TableColumns';
import { useModalQueryState } from '@/Hooks/useModalState';

function MyBeltTimerTable() {
	const { t } = useTranslation();
	const { characterID } = useParams();
	const { activeModal, activeEntityId, openModal, closeModal } = useModalQueryState();

	// Load Belt Timers data
	const { data: timerData, isError: isErrorTimers, isFetching: isFetchingTimers } = useQuery({
		queryKey: queryKeys.myBeltTimers(Number(characterID)),
		queryFn: () => loadMyBeltTimers(Number(characterID)),
		refetchOnWindowFocus: false,
		enabled: !!characterID,
	});

	const activeTimer = useMemo(
		() => timerData?.find((timer) => timer.public_id === activeEntityId) ?? null,
		[timerData, activeEntityId],
	);

	// Define table columns for belt timers
	const timerColumns = useMemo(
		() =>
			getBeltTimerColumns(
				t,
				(timer: BeltTimer) => timer,
				(actionId: string | null, row?: BeltTimer) => {
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
				data={timerData ?? []}
				isError={isErrorTimers}
				isFetching={isFetchingTimers}
				columns={timerColumns}
			/>
			<BeltRadarModals
				session={activeTimer}
				modalAction={activeModal}
				setModalAction={(action) => (!action ? closeModal() : openModal(action))}
				t={t}
				queryKey={queryKeys.myBeltTimers(Number(characterID))}
			/>
		</>
	);
}

export default MyBeltTimerTable;
