// AA Belt Radar
import { queryKeys } from '@/Api/query';
import type { SessionStats } from '@/Api/schema';
import BaseModal from '@/Components/Modals/BaseModal';
import { useApproveMutation } from '@/Components/Modals/BeltRadarQuery';

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
                    children={<div>{deleteTimerAction.text}</div>}
                />
            )}
            {createTimerAction && (
                <BaseModal
                    data={createTimerAction}
                    showModal={activeModal === createTimerAction.modal_id}
                    setShowModal={(show) => setActiveModal(show ? createTimerAction.modal_id : null)}
                    onApprove={({ url }) => handleApprove(url)}
                    isPending={approveMutation.isPending}
                    children={<div>{createTimerAction.text}</div>}
                />
            )}
        </>
    );
}

export default SessionModals;
