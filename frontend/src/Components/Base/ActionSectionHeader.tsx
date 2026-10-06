// Third Party
import { useQuery } from '@tanstack/react-query';
import { Plus } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import { loadMenu } from '@/Api/ApiCalls';
import { queryKeys } from "@/Api/query";
import BaseModal from '@/Components/Base/BaseModal';
import { useFormApproveMutation } from '@/Components/Base/BaseModal/BaseModalQuery';
import { useModalQueryState } from '@/Components/Base/BaseModal/useModalState';
import type { SectionHeaderProps } from '@/Components/Base/SectionHeaderProps';
import { IconButton } from '@/Components/Icons/Icons';

export function ActionSectionHeader({
    name,
    queryKey,
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

    return (
        <>
            <section className="aa-panel br-header" aria-labelledby="section-heading">
                <h3 id="section-heading" className="aa-section-title mb-0">{name}</h3>
                {action && (
                    <div className="br-toolbar">
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
