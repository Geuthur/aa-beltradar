// Third Party
import { useQuery } from '@tanstack/react-query';
import { BaseModal, useFormApproveMutation, useModalQueryState } from "aa-geuthur-react";
import { Plus } from 'lucide-react';
import { Card } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMenu } from '@/Api/ApiCalls';
import { listQueryKeys, queryKeys } from "@/Api/query";
import type { SectionHeaderProps } from '@/Components/Base/SectionHeaderProps';
import { IconButton } from '@/Components/Icons/Icons';
import { useModalData } from '@/Components/Modals/modalConfig';

export function ActionSectionHeader({
    name,
    queryKey = listQueryKeys,
    modalKey,
    buttonTitle,
    buttonIcon = <Plus size={14} aria-hidden="true" />,
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
    const modalData = useModalData(action);

    return (
        <>
            <Card className="border-0 shadow-sm mb-3" aria-labelledby="section-heading">
                <Card.Header className="bg-primary text-light rounded d-flex justify-content-between align-items-center">
                    <h3 id="section-heading" className="mb-0">{name}</h3>
                    {action && (
                        <div className="text-end d-flex align-items-center gap-2">
                            <IconButton
                                icon={buttonIcon}
                                color="success"
                                onClick={() => {
                                    openModal(action.modal_id);
                                }}
                                title={buttonTitle ?? t("Create")}
                            />
                        </div>
                    )}
                </Card.Header>
            </Card>
            {action && modalData && children && (
                <BaseModal
                    variant="confirm"
                    bodyClassName="aa-panel"
                    data={modalData}
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
