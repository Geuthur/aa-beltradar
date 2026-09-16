// React
import { useState } from 'react';

// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMenu } from '@/Api/BeltRadar';
import CreateSessionForm from '@/Components/Forms/CreateSessionForm';
import { IconButton } from '@/Components/Icons/Icons';
import BaseModal from '@/Components/Modals/BaseModal';
import { useFormApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import { queryKeys } from '@/Components/Props/BeltRadarQuery';

function BeltRadarHeader({ name }: { name: string }) {
    const { t } = useTranslation();
    const formApproveMutation = useFormApproveMutation();
    const [showModal, setModalAction] = useState<string | null>(null);

	// Load Belt Radar public sessions data
	const { data: menuData } = useQuery({
		queryKey: queryKeys.Menu,
		queryFn: () => loadMenu(),
		refetchOnWindowFocus: false,
	});
    const createAction = menuData?.modals?.create_session

    return (
        <>
            <section className="card" aria-labelledby="session-heading">
                <div className="card-header bg-primary rounded">
                    <div className="d-flex justify-content-between align-items-center">
                        <h3 id="session-heading">{name}</h3>
                        {createAction && (
                            <IconButton
                                icon="fas fa-plus"
                                color="success"
                                onClick={() => {
                                    setModalAction(createAction.modal_id);
                                }}
                                title={t("Create Session")}
                                classProps="me-2 text-end"
                            />
                        )}
                    </div>
                </div>
            </section>
            {createAction && (
                <BaseModal
                    data={createAction}
                    showModal={showModal === createAction.modal_id}
                    onApprove={(args) => formApproveMutation.mutateAsync(args)}
                    isPending={formApproveMutation.isPending}
                    setShowModal={(show) => setModalAction(show ? createAction.modal_id : null)}
                    children={CreateSessionForm}
                />
            )}
        </>
    );
};

export default BeltRadarHeader;
