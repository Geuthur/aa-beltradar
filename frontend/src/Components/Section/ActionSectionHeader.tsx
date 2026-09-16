// Third Party
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMenu } from '@/Api/BeltRadar';
import { queryKeys } from "@/Api/query";
import { IconButton } from '@/Components/Icons/Icons';
import BaseModal from '@/Components/Modals/BaseModal';
import { useFormApproveMutation } from '@/Components/Modals/BeltRadarQuery';
import type { SectionHeaderProps } from '@/Components/Section/SectionHeaderProps';
import { useModalQueryState } from '@/Hooks/useModalState';

export function ActionSectionHeader({
    name,
    queryKey,
    modalKey,
    buttonTitle,
    buttonIcon = "fas fa-plus",
    validate,
    children,
}: SectionHeaderProps) {
    const { t } = useTranslation();
    const formApproveMutation = useFormApproveMutation(queryKey);
    const { activeModal, openModal, closeModal } = useModalQueryState();

    const { data: menuData } = useQuery({
        queryKey: queryKeys.Menu,
        queryFn: () => loadMenu(),
        refetchOnWindowFocus: false,
    });

    const action = modalKey ? menuData?.modals?.[modalKey] : null;

    return (
        <>
            <section className="card" aria-labelledby="section-heading">
                <div className="card-header bg-primary rounded">
                    <div className="d-flex justify-content-between align-items-center">
                        <h3 id="session-heading">{name}</h3>
                        {action && (
                            <IconButton
                                icon={buttonIcon}
                                color="success"
                                onClick={() => {
                                    openModal(action.modal_id);
                                }}
                                title={buttonTitle ?? t("Create")}
                                classProps="me-2 text-end"
                            />
                        )}
                    </div>
                </div>
            </section>
            {action && children && (
                <BaseModal
                    data={action}
                    showModal={activeModal === action.modal_id}
                    onApprove={(args) => formApproveMutation.mutateAsync(args)}
                    isPending={formApproveMutation.isPending}
                    setShowModal={(show) => (!show ? closeModal() : openModal(action.modal_id))}
                    validate={validate}
                    children={children}
                />
            )}
        </>
    );
}

export default ActionSectionHeader;
