// React
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { getSnapshotColumns } from "@/Components/Tables/TableColumns";
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadSnapshot } from '@/Api/BeltRadar';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import BaseTable from '@/Components/Tables/BaseTable';

function SessionSnapshotTable() {
	const { t } = useTranslation();
	const { publicID } = useParams();

	// Load Snapshot data
	const { data: snapshotData, isError: isErrorSnapshot, isFetching: isFetchingSnapshot } = useQuery({
		queryKey: queryKeys.Snapshot(String(publicID)),
		queryFn: () => loadSnapshot(String(publicID)),
		refetchOnWindowFocus: false,
		enabled: !!publicID,
	});
	return (
		<>
			<div className="card card-body mt-2">
				<BaseTable
					data={snapshotData?.ore_list ?? []}
					isError={isErrorSnapshot}
					isFetching={isFetchingSnapshot}
					columns={getSnapshotColumns(t)}
				/>
			</div>
		</>
	);
}

export default SessionSnapshotTable;
