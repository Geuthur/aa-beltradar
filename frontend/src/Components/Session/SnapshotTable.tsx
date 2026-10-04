// React
import { useState } from 'react';
import { useParams } from 'react-router-dom';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadSnapshot } from '@/Api/BeltRadar';
import { queryKeys, SESSION_REFETCH_INTERVAL_MS } from "@/Api/query";
import AddSnapshotForm from '@/Components/Forms/AddSnapshotForm';
import { validateAddSnapshotForm } from '@/Components/Forms/validation';
import BaseModal, { ModalSize } from '@/Components/Modals/BaseModal';
import { useApproveMutation, useFormApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import { getModalConfig } from '@/Components/Modals/modalConfig';
import BaseTable from '@/Components/Tables/BaseTable';
import { SnapshotButtons, SnapshotSelect } from '@/Components/Tables/Snapshot';
import { getSnapshotColumns } from "@/Components/Tables/TableColumns";

function SessionSnapshotTable() {
	const { t } = useTranslation();
	const { publicID } = useParams();
	const [showAddModal, setShowAddModal] = useState(false);
	const [showDeleteModal, setShowDeleteModal] = useState(false);
	const [selectedSnapshotId, setSelectedSnapshotId] = useState<string | null>(null);

	const sessionKey = queryKeys.Session(String(publicID));
	const snapshotQueryKey = queryKeys.Snapshot(String(publicID), selectedSnapshotId);
	const snapshotBaseKey = ["Snapshot", String(publicID)];

	// Load Snapshot data
	const { data: snapshotData, isError: isErrorSnapshot, isFetching: isFetchingSnapshot } = useQuery({
		queryKey: snapshotQueryKey,
		queryFn: () => loadSnapshot(String(publicID), selectedSnapshotId),
		refetchOnWindowFocus: false,
		refetchInterval: SESSION_REFETCH_INTERVAL_MS,
		enabled: !!publicID,
	});

	const formApproveMutation = useFormApproveMutation([snapshotBaseKey, sessionKey]);
	const approveMutation = useApproveMutation([snapshotBaseKey, sessionKey]);

	const addAction = snapshotData?.actions?.create;
	const deleteAction = snapshotData?.actions?.delete;
	const snapshots = snapshotData?.snapshots ?? [];

	const handleDeleteApprove = async (url: string) => {
		await approveMutation.mutateAsync(url);
		setSelectedSnapshotId(null);
	};

	return (
		<>
			<section className="d-flex flex-column gap-2" aria-label={t("Ore Snapshot")}>
				<div className="aa-panel d-flex flex-wrap align-items-center justify-content-between gap-2">
					<div className="d-flex align-items-center gap-2">
						<span className="aa-section-title">{t("Ore Snapshot")}</span>
						<SnapshotSelect
							snapshots={snapshots}
							selectedSnapshotId={selectedSnapshotId}
							fallbackIdentifier={snapshotData?.snapshot?.identifier}
							onSelect={setSelectedSnapshotId}
						/>
					</div>
					<SnapshotButtons
						addAction={addAction}
						deleteAction={deleteAction}
						onAddClick={() => setShowAddModal(true)}
						onDeleteClick={() => setShowDeleteModal(true)}
					/>
				</div>
				<BaseTable
					data={snapshotData?.ore_list ?? []}
					isError={isErrorSnapshot}
					isFetching={isFetchingSnapshot}
					columns={getSnapshotColumns(t)}
					itemLabel={t("ores")}
				/>
			</section>
			{addAction && (
				<BaseModal
					data={addAction}
					size={ModalSize.extraLarge}
					showModal={showAddModal}
					setShowModal={setShowAddModal}
					onApprove={(args) => formApproveMutation.mutateAsync(args)}
					isPending={formApproveMutation.isPending}
					validate={validateAddSnapshotForm}
					children={({ formData, onChange }) => (
						<AddSnapshotForm
							formData={formData}
							onChange={onChange}
						/>
					)}
				/>
			)}
			{deleteAction && (
				<BaseModal
					data={deleteAction}
					showModal={showDeleteModal}
					setShowModal={setShowDeleteModal}
					onApprove={({ url }) => handleDeleteApprove(url)}
					isPending={approveMutation.isPending}
					children={<div>{getModalConfig(t, deleteAction.modal_id).text}</div>}
				/>
			)}
		</>
	);
}

export default SessionSnapshotTable;
