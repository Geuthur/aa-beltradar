// React
import { useParams } from 'react-router-dom'

// Third Party
import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadSnapshot } from '@/Api/BeltRadar'
import type { OreSchema } from '@/Components/Props/BeltRadarProps'
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import TableWrapper from '@/Components/Tables/TableWrapper'

function SessionSnapshotTable() {
	const { t } = useTranslation();
	const { publicID } = useParams();
	//const [snapshot, setSnapshot] = useState<SessionSnapshot | Record<string, never>>({});
	//const [modalAction, setModalAction] = useState<string | null>(null);

	// Load Snapshot data
	const { data: snapshotData, isError: isErrorSnapshot, isFetching: isFetchingSnapshot } = useQuery({
		queryKey: queryKeys.Snapshot(String(publicID)),
		queryFn: () => loadSnapshot(String(publicID)),
		refetchOnWindowFocus: false,
		enabled: !!publicID,
	});

	// Define table columns for the my belt radar sessions
	const columnHelper = createColumnHelper<OreSchema>();
	const columns = [
		columnHelper.accessor('name', {
			header: t("Ore"),
		}),
		columnHelper.accessor('units', {
			header: t("Units Left"),
		}),
		columnHelper.accessor('volume_m3', {
			header: t("Volume Left (m³)"),
		}),
		columnHelper.accessor('price_isk', {
			header: t("Price (ISK/m³)"),
		}),
		columnHelper.accessor('price_compressed', {
			header: t("Price Compressed"),
		}),
		columnHelper.accessor('income_cmp_per_h', {
			header: t("Income Compressed (ISK/h)"),
		})
	]

	return (
		<>
			<div className="card card-body mt-2">
				<TableWrapper
					data={snapshotData?.ore_list ?? []}
					isError={isErrorSnapshot}
					isFetching={isFetchingSnapshot}
					columns={columns}
				/>
			</div>
		</>

	)
}

export default SessionSnapshotTable
