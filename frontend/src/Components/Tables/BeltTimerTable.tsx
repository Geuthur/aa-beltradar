// React
import { useMemo } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadBeltTimers } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import type { BeltTimer } from "@/Api/schema";
import { useModalQueryState } from '@/Components/Modals/BaseModal/useModalState';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import BaseTable from '@/Components/Tables/BaseTable';
import { getBeltTimerColumns } from '@/Components/Tables/TableColumns';

function BeltTimerTable() {
	const { t } = useTranslation();
	const { activeModal, activeEntityId, openModal, closeModal } = useModalQueryState();

	// Load Belt Timers data
	const { data: timerData, isError: isErrorTimers, isFetching: isFetchingTimers } = useQuery({
		queryKey: queryKeys.beltTimer,
		queryFn: () => loadBeltTimers(),
		refetchOnWindowFocus: false,
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
				queryKey={queryKeys.beltTimer}
			/>
		</>
	);
}

export default BeltTimerTable;
