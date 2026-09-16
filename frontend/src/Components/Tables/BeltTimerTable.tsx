// React
import { useMemo, useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadBeltTimers } from '@/Api/BeltRadar';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { BeltTimer } from '@/Components/Props/BeltRadarProps';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import BaseTable from '@/Components/Tables/BaseTable';
import { getBeltTimerColumns } from '@/Components/Tables/TableColumns';

function BeltTimerTable() {
	const { t } = useTranslation();
	const [belttimer, setBeltTimer] = useState<BeltTimer | Record<string, never>>({});
	const [modalAction, setModalAction] = useState<string | null>(null);

	// Load Belt Timers data
	const { data: timerData, isError: isErrorTimers, isFetching: isFetchingTimers } = useQuery({
		queryKey: queryKeys.beltTimer,
		queryFn: () => loadBeltTimers(),
		refetchOnWindowFocus: false,
	});

	// Define table columns for belt timers
	const timerColumns = useMemo(
		() => getBeltTimerColumns(t, setBeltTimer, setModalAction),
		[t],
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
				session={belttimer as BeltTimer}
				modalAction={modalAction}
				setModalAction={setModalAction}
				t={t}
				queryKey={queryKeys.beltTimer}
			/>
		</>
	);
}

export default BeltTimerTable;
