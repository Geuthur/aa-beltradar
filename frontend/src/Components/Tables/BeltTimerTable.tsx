// Third Party
import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadBeltTimers } from '@/Api/BeltRadar'
import type { components } from '@/Api/OpenApi'
import { renderHtml } from '@/Components/Helpers/functions';
import TableWrapper from '@/Components/Tables/TableWrapper';

type BeltTimer = components['schemas']['BeltTimerSchema']

function BeltTimerTable() {
	const { t } = useTranslation();

	// Load Belt Timers data
	const { data: timerData, isError: isErrorTimers, isFetching: isFetchingTimers } = useQuery({
		queryKey: ["belt-timers"],
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
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
		timerColumnHelper.accessor('html', {
			header: t("Actions"),
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
	]

	return (
		<TableWrapper
			data={timerData ?? []}
			isError={isErrorTimers}
			isFetching={isFetchingTimers}
			columns={timerColumns}
		/>
	)
}

export default BeltTimerTable
