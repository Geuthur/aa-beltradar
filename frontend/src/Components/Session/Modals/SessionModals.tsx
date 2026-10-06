// React
import { useState } from 'react';

// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { queryKeys } from '@/Api/query';
import type { SessionStats } from '@/Api/schema';
import BaseModal from '@/Components/Base/BaseModal';
import { useApproveMutation } from '@/Components/Base/BaseModal/BaseModalQuery';
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
    const [cachedSession, setCachedSession] = useState(session);
    if (session && session !== cachedSession) {
        setCachedSession(session);
    }
    const effectiveSession = session ?? cachedSession;

    const sessionKey = queryKeys.Session(String(effectiveSession?.public_id));
    const approveMutation = useApproveMutation([sessionKey, queryKeys.beltTimer]);

    const deleteTimerAction = effectiveSession?.actions?.delete;
    const createTimerAction = effectiveSession?.actions?.create;

    const handleApprove = async (url: string) => {
        await approveMutation.mutateAsync(url);
        setActiveModal(null);
    };

    return (
        <>
            {deleteTimerAction && (
                <BaseModal
                    data={deleteTimerAction}
                    variant='confirm'
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
                    variant='confirm'
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
