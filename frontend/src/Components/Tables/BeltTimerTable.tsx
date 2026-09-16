// React
import { useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadBeltTimers } from '@/Api/BeltRadar'
import { renderHtml } from '@/Components/Helpers/functions';
import { BeltTimerTableButtons } from '@/Components/Icons/Icons';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { BeltTimer } from '@/Components/Props/BeltRadarProps'
import { queryKeys } from '@/Components/Props/BeltRadarQuery'
import TableWrapper from '@/Components/Tables/TableWrapper';

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
	const timerColumnHelper = createColumnHelper<BeltTimer>();
	const timerColumns = [
		timerColumnHelper.accessor('public_id', {
			header: t("Public ID"),
		}),
		timerColumnHelper.accessor('belt_name', {
			header: t("Belt Name"),
		}),
		timerColumnHelper.accessor('belt_size', {
			header: t("Belt Size"),
		}),
		timerColumnHelper.accessor('belt_type', {
			header: t("Belt Type"),
		}),
		timerColumnHelper.accessor('eta.display', {
			header: t("ETA"),
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
		timerColumnHelper.accessor('public.display', {
			header: t("Public"),
			enableSorting: false,
			enableColumnFilter: false,
			enableGlobalFilter: false,
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
		timerColumnHelper.accessor('actions', {
			header: t("Actions"),
			enableSorting: false,
			enableColumnFilter: false,
			enableGlobalFilter: false,
			cell: (cell) => {
				return (
					<BeltTimerTableButtons
						cell={cell}
						setTimer={setBeltTimer}
						setModalAction={setModalAction}
					/>
				);
			},
		})
	]

	return (
		<>
			<TableWrapper
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
	)
}

export default BeltTimerTable
