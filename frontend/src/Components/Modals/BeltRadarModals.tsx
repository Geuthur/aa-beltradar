// React
import { useMemo } from 'react';

// Third Party
import type { QueryKey } from '@tanstack/react-query';

// AA Belt Radar
import type { SessionItem, BeltTimer } from "@/Api/schema";
import CreateBeltTimerForm from '@/Components/Forms/CreateBeltTimerForm';
import {
	getBeltSizeValue,
	getBeltTypeValue,
	validateBeltTimerForm,
} from '@/Components/Forms/validation';
import BaseModal from '@/Components/Modals/BaseModal';
import { useApproveMutation, useFormApproveMutation } from '@/Components/Modals/BeltRadarQuery';

export interface BeltRadarModalsProps {
	session?: SessionItem | BeltTimer | null;
	modalAction: string | null;
	setModalAction: (action: string | null) => void;
	t: (key: string) => string;
	queryKey: QueryKey;
}

function BeltRadarModals({ session: data, modalAction, setModalAction, queryKey }: BeltRadarModalsProps) {
	const approveMutation = useApproveMutation(queryKey);
	const formApproveMutation = useFormApproveMutation(queryKey);

	const isBeltTimer = data ? 'belt_id' in data : false;
	const isSessionLinked = isBeltTimer ? Boolean((data as BeltTimer).has_session) : false;

	const timerInitialFormData = useMemo(() => {
		if (!data || !isBeltTimer) return undefined;
		const timer = data as BeltTimer;
		return {
			belt_id: timer.belt_id ?? '',
			belt_name: timer.belt_name ?? '',
			belt_type: getBeltTypeValue(timer.belt_type),
			belt_size: getBeltSizeValue(timer.belt_size),
			is_public: Boolean(timer.public?.raw ?? false),
		};
	}, [data, isBeltTimer]);

	if (!data) {
		return null;
	}

	const updateAction = data.actions?.update;
	const deleteAction = data.actions?.delete;

	return (
		<>
			{updateAction && (
				isBeltTimer ? (
					<BaseModal
						data={updateAction}
						showModal={modalAction === updateAction.modal_id}
						onApprove={(args) => formApproveMutation.mutateAsync(args)}
						isPending={formApproveMutation.isPending}
						setShowModal={(show) => setModalAction(show ? updateAction.modal_id : null)}
						initialFormData={timerInitialFormData}
						validate={validateBeltTimerForm}
						children={({ formData, onChange }) => (
							<CreateBeltTimerForm
								formData={formData}
								onChange={onChange}
								isEdit={true}
								isSessionLinked={isSessionLinked}
							/>
						)}
					/>
				) : (
					<BaseModal
						data={updateAction}
						showModal={modalAction === updateAction.modal_id}
						onApprove={({ url }) => approveMutation.mutateAsync(url)}
						isPending={approveMutation.isPending}
						setShowModal={(show) => setModalAction(show ? updateAction.modal_id : null)}
						children={<div>{updateAction.text}</div>}
					/>
				)
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
	);
}

export default BeltRadarModals;
