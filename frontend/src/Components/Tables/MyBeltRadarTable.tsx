// React
import { useParams } from 'react-router-dom'

// Third Party
import { useQuery } from '@tanstack/react-query'
import { createColumnHelper } from "@tanstack/react-table";
import { useTranslation } from 'react-i18next'
import { useState } from 'react';
import { IconButton } from "@/Components/Tables/Icons/Icons";

// AA Belt Radar
import { loadMySessions } from '@/Api/BeltRadar'
import type { components } from '@/Api/OpenApi'
import { formatDate, renderHtml } from '@/Components/Helpers/functions';
import BeltRadarModals from '@/Components/Modals/BeltRadarModals';
import TableWrapper from '@/Components/Tables/TableWrapper'

type Session = components['schemas']['BeltSurveySessionSchema']

function MyBeltRadarTable() {
	const { t } = useTranslation();
	const { characterID } = useParams();
	const [session, setSession] = useState<Session | Record<string, never>>({});
	const [modalAction, setModalAction] = useState<'approve' | 'delete' | null>(null);

	// Load My Belt Radar sessions data
	const { data: sessionData, isError: isErrorSessions, isFetching: isFetchingSessions } = useQuery({
		queryKey: ["sessions"],
		queryFn: () => loadMySessions(Number(characterID)),
		refetchOnWindowFocus: false,
		enabled: !!characterID,
	});

	// Define table columns for the my belt radar sessions
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
		columnHelper.accessor('owner', {
			header: t("Owner"),
			cell: ({ getValue }) => renderHtml(getValue<string>() || '-'),
		}),
		columnHelper.accessor('public.display', {
			header: t("Public"),
			cell: ({ getValue }) => renderHtml(getValue<string>()),
		}),
		columnHelper.accessor('html', {
			header: t("Actions"),
			cell: (cell) => {
				return (
					<>
						<IconButton
							icon="fa-solid fa-check"
							onClick={() => {
								setSession(cell.row.original);
								setModalAction('approve');
							}}
							title={t("Approve Session")}
							color="success"
						/>
						<IconButton
							icon="fa-solid fa-trash"
							onClick={() => {
								setSession(cell.row.original);
								setModalAction('delete');
							}}
							title={t("Delete Session")}
							color="danger"
						/>
					</>
				);
			},
		}),
	]

	return (
		<>
			<TableWrapper
				columns={columns}
				data={sessionData ?? []}
				isError={isErrorSessions}
				isFetching={isFetchingSessions}
			/>
			<BeltRadarModals
				session={session}
				modalAction={modalAction}
				setModalAction={setModalAction}
				t={t}
			/>
		</>

	)
}

export default MyBeltRadarTable
