// Third Party
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { ModalSchema } from '@/Api/schema';
import { IconButton } from '@/Components/Icons/Icons';
import { renderTooltip } from '@/Components/Tables/BaseTable/tableHelper';

export interface SessionHeaderButtonsProps {
    hasTimer: boolean;
    deleteTimerAction?: ModalSchema | null;
    createTimerAction?: ModalSchema | null;
    onAction: (modalId: string | null) => void;
}

export function SessionHeaderButtons({
    hasTimer,
    deleteTimerAction,
    createTimerAction,
    onAction,
}: SessionHeaderButtonsProps) {
    const { t } = useTranslation();

    // Translations for tooltips and titles
    const tBeltTimerActive = t("Belt Timer active");
    const tDeleteBeltTimer = t("Delete Belt Timer");
    const tCreateBeltTimer = t("Create Belt Timer");

    if (hasTimer) {
        return (
            <div className="d-flex align-items-center gap-2">
                {renderTooltip(
                    tBeltTimerActive,
                    <span className="text-white d-inline-flex align-items-center" style={{ fontSize: "1.2rem" }}>
                        <i className="fa-solid fa-stopwatch"></i>
                    </span>
                )}
                {deleteTimerAction && (
                    <IconButton
                        icon={deleteTimerAction.icon ?? "fa-solid fa-trash"}
                        color={deleteTimerAction.color ?? "danger"}
                        title={deleteTimerAction.title ?? tDeleteBeltTimer}
                        onClick={() => onAction(deleteTimerAction.modal_id)}
                        classProps="me-0"
                    />
                )}
            </div>
        );
    }

    if (createTimerAction) {
        return (
            <IconButton
                icon={createTimerAction.icon ?? "fa-solid fa-plus"}
                color={createTimerAction.color ?? "success"}
                title={createTimerAction.title ?? tCreateBeltTimer}
                onClick={() => onAction(createTimerAction.modal_id)}
                classProps="me-0"
            />
        );
    }

    return null;
}

export default SessionHeaderButtons;
