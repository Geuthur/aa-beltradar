// Third Party
import type { QueryKey } from '@tanstack/react-query';

// AA Belt Radar
import BaseModal from '@/Components/Modals/BaseModal';
import { useApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import type { Session, BeltTimer } from '@/Components/Props/BeltRadarProps';

export interface BeltRadarModalsProps {
	session: Session | BeltTimer;
	modalAction: string | null;
	setModalAction: (action: string | null) => void;
	t: (key: string) => string;
	queryKey: QueryKey;
}

function BeltRadarModals({ session: data, modalAction, setModalAction, queryKey }: BeltRadarModalsProps) {
	const approveMutation = useApproveMutation(queryKey);
	const updateAction = data.actions?.update;
	const deleteAction = data.actions?.delete;
	return (
		<>
			{updateAction && (
				<BaseModal
					data={updateAction}
					showModal={modalAction === updateAction.modal_id}
					onApprove={({ url }) => approveMutation.mutateAsync(url)}
					isPending={approveMutation.isPending}
					setShowModal={(show) => setModalAction(show ? updateAction.modal_id : null)}
					children={<div>{updateAction.text}</div>}
				/>
			)}
			{deleteAction && (
				<BaseModal
					data={deleteAction}
					showModal={modalAction === deleteAction.modal_id}
					onApprove={({ url }) => approveMutation.mutateAsync(url)}
					isPending={approveMutation.isPending}
					setShowModal={(show) => setModalAction(show ? deleteAction.modal_id : null)}
					children={<div>{deleteAction.text}</div>}
				/>
			)}
		</>
	)
}

export default BeltRadarModals
