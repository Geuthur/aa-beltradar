// Third Party
import { Timer } from 'lucide-react';
import { useTranslation } from 'react-i18next';

// AA Belt Radar
import type { ModalSchema } from '@/Api/schema';
import { renderTooltip } from '@/Components/Base/BaseTable/tableHelper';
import { ActionButton } from '@/Components/Icons/Icons';

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

    if (hasTimer) {
        return (
            <div className="d-flex align-items-center gap-2">
                {renderTooltip(
                    tBeltTimerActive,
                    <span className="br-timer-icon">
                        <Timer size={20} aria-hidden="true" />
                    </span>
                )}
                {deleteTimerAction && (
                    <ActionButton
                        action={deleteTimerAction}
                        onClick={() => onAction(deleteTimerAction.modal_id)}
                        classProps="me-0"
                    />
                )}
            </div>
        );
    }

    if (createTimerAction) {
        return (
            <ActionButton
                action={createTimerAction}
                onClick={() => onAction(createTimerAction.modal_id)}
                classProps="me-0"
            />
        );
    }

    return null;
}

export default SessionHeaderButtons;
