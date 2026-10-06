// React
import { useMemo, useState } from 'react';

// Third Party
import type { QueryKey } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { SessionItem, BeltTimer } from "@/Api/schema";
import BaseModal from '@/Components/Base/BaseModal';
import { useApproveMutation, useFormApproveMutation } from '@/Components/Base/BaseModal/BaseModalQuery';
import CreateBeltTimerForm from '@/Components/Forms/CreateBeltTimerForm';
import {
	getBeltSizeValue,
	getBeltTypeValue,
	validateBeltTimerForm,
} from '@/Components/Forms/validation';
import { getModalConfig } from '@/Components/Modals/modalConfig';

export interface BeltRadarModalsProps {
	session?: SessionItem | BeltTimer | null;
	modalAction: string | null;
	setModalAction: (action: string | null) => void;
	t: (key: string) => string;
	queryKey: QueryKey;
}

function BeltRadarModals({ session: data, modalAction, setModalAction, queryKey }: BeltRadarModalsProps) {
	const { t } = useTranslation();
	const approveMutation = useApproveMutation(queryKey);
	const formApproveMutation = useFormApproveMutation(queryKey);

	const [cachedData, setCachedData] = useState(data);
	if (data && data !== cachedData) {
		setCachedData(data);
	}
	const effectiveData = data ?? cachedData;

	const isBeltTimer = effectiveData ? 'belt_id' in effectiveData : false;
	const isSessionLinked = isBeltTimer ? Boolean((effectiveData as BeltTimer).has_session) : false;

	const timerInitialFormData = useMemo(() => {
		if (!effectiveData || !isBeltTimer) return undefined;
		const timer = effectiveData as BeltTimer;
		return {
			belt_id: timer.belt_id ?? '',
			belt_name: timer.belt_name ?? '',
			belt_type: getBeltTypeValue(timer.belt_type),
			belt_size: getBeltSizeValue(timer.belt_size),
			is_public: Boolean(timer.public?.raw ?? false),
		};
	}, [effectiveData, isBeltTimer]);

	if (!effectiveData) {
		return null;
	}

	const updateAction = effectiveData.actions?.update;
	const deleteAction = effectiveData.actions?.delete;

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
						children={<div>{getModalConfig(t, updateAction.modal_id).text}</div>}
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
					children={<div>{getModalConfig(t, deleteAction.modal_id).text}</div>}
				/>
			)}
		</>
	);
}

export default BeltRadarModals;
