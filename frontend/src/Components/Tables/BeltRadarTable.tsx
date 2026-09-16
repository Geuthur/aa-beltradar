// React
import { useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from 'react-i18next'

// AA Belt Radar
import { loadPublicSessions } from '@/Api/BeltRadar'
import { formatDate, renderHtml } from '@/Components/Helpers/functions';
import { BeltRadarTableButtons } from "@/Components/Icons/Icons";
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import type { Session } from '@/Components/Props/BeltRadarProps';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';
import TableWrapper from '@/Components/Tables/TableWrapper';

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
	const columnHelper = createColumnHelper<Session>();
	const columns = [
		columnHelper.accessor('public_id', {
			header: t("Public ID"),
		}),
		columnHelper.accessor('name', {
			header: t("Name"),
		}),
		columnHelper.accessor('created_at', {
			header: t("Created At"),
			cell: ({ getValue }) => formatDate(getValue())
		}),
		columnHelper.accessor('owner.portrait', {
			header: t("Owner"),
			cell: ({ getValue }) => renderHtml(getValue<string>() || '-'),
		}),
		columnHelper.accessor('public.display', {
			header: t("Public"),
			enableSorting: false,
			enableColumnFilter: false,
			enableGlobalFilter: false,
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
		columnHelper.accessor('actions', {
			header: t("Actions"),
			enableSorting: false,
			enableColumnFilter: false,
			enableGlobalFilter: false,
			cell: (cell) => {
				return (
					<BeltRadarTableButtons
						cell={cell}
						setSession={setSession}
						setModalAction={setModalAction}
					/>
				);
			},
		})
	]

	return (
		<>
			<TableWrapper
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
	)
}

export default BeltRadarTable
