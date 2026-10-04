// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { queryKeys } from '@/Api/query';
import type { SessionStats } from '@/Api/schema';
import BaseModal from '@/Components/Modals/BaseModal';
import { useApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import { getModalConfig } from '@/Components/Modals/modalConfig';

export interface SessionModalsProps {
    session?: SessionStats | null;
    activeModal: string | null;
    setActiveModal: (action: string | null) => void;
}

export function SessionModals({
    session,
    activeModal,
    setActiveModal,
}: SessionModalsProps) {
    const { t } = useTranslation();
    const sessionKey = queryKeys.Session(String(session?.public_id));
    const approveMutation = useApproveMutation([sessionKey, queryKeys.beltTimer]);

    const deleteTimerAction = session?.actions?.delete;
    const createTimerAction = session?.actions?.create;

    const handleApprove = async (url: string) => {
        await approveMutation.mutateAsync(url);
        setActiveModal(null);
    };

    return (
        <>
            {deleteTimerAction && (
                <BaseModal
                    data={deleteTimerAction}
                    showModal={activeModal === deleteTimerAction.modal_id}
                    setShowModal={(show) => setActiveModal(show ? deleteTimerAction.modal_id : null)}
                    onApprove={({ url }) => handleApprove(url)}
                    isPending={approveMutation.isPending}
                    children={<div>{getModalConfig(t, deleteTimerAction.modal_id).text}</div>}
                />
            )}
            {createTimerAction && (
                <BaseModal
                    data={createTimerAction}
                    showModal={activeModal === createTimerAction.modal_id}
                    setShowModal={(show) => setActiveModal(show ? createTimerAction.modal_id : null)}
                    onApprove={({ url }) => handleApprove(url)}
                    isPending={approveMutation.isPending}
                    children={<div>{getModalConfig(t, createTimerAction.modal_id).text}</div>}
                />
            )}
        </>
    );
}

export default SessionModals;
