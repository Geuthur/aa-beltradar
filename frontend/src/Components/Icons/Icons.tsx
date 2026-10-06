// React
import type { ReactNode } from "react";
import { useNavigate } from "react-router-dom";

// Third Party
import type { CellContext } from "@tanstack/react-table";
import { Eye } from "lucide-react";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import type { BeltTimer, ModalSchema, Session } from "@/Api/schema";
import { renderTooltip } from "@/Components/Base/BaseTable/tableHelper";
import { getModalConfig } from "@/Components/Modals/modalConfig";

export interface ButtonProps {
    icon: ReactNode;
    onClick: () => void;
    title: string;
    color: string;
    classProps?: string;
}

export function IconButton({ icon, onClick, title, color, classProps }: ButtonProps) {
    return (
        <>
            {renderTooltip(
                title,
                <button
                    type="button"
                    onClick={onClick}
                    aria-label={title}
                    className={`aa-btn aa-btn-sm aa-btn-${color} me-2 ${classProps ?? ""}`}>
                    {icon}
                </button>
            )}
        </>
    );
}

export interface ActionButtonProps {
    action: ModalSchema;
    onClick: () => void;
    classProps?: string;
}

/** Button for an action of the API; icon, title and color come from the modal config. */
export function ActionButton({ action, onClick, classProps }: ActionButtonProps) {
    const { t } = useTranslation();
    const { icon, title, color } = getModalConfig(t, action.modal_id);
    return (
        <IconButton
            icon={icon}
            title={title}
            color={color}
            onClick={onClick}
            classProps={classProps}
        />
    );
}

export interface EntityWithActions {
    public_id: string;
    has_session?: boolean;
    actions?: {
        update?: ModalSchema | null;
        delete?: ModalSchema | null;
    } | null;
}

export interface EntityTableActionsProps<T extends EntityWithActions> {
    cell: CellContext<T, unknown>;
    onSelectEntity?: (entity: T) => void;
    setModalAction: (action: string | null, entity?: T) => void;
    showViewSession?: boolean;
}

export function EntityTableActions<T extends EntityWithActions>({
    cell,
    onSelectEntity,
    setModalAction,
    showViewSession,
}: EntityTableActionsProps<T>) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const row = cell.row.original;
    const updateAction = row.actions?.update;
    const deleteAction = row.actions?.delete;

    const canViewSession =
        showViewSession !== undefined
            ? showViewSession
            : row.has_session !== undefined
                ? Boolean(row.has_session)
                : true;

    return (
        <>
            {canViewSession && (
                <IconButton
                    icon={<Eye size={14} aria-hidden="true" />}
                    onClick={() => {
                        navigate("/beltradar/session/" + row.public_id + "/");
                    }}
                    title={t("View Session")}
                    color="primary"
                />
            )}
            {updateAction && (
                <ActionButton
                    action={updateAction}
                    onClick={() => {
                        onSelectEntity?.(row);
                        setModalAction(updateAction.modal_id, row);
                    }}
                />
            )}
            {deleteAction && (
                <ActionButton
                    action={deleteAction}
                    onClick={() => {
                        onSelectEntity?.(row);
                        setModalAction(deleteAction.modal_id, row);
                    }}
                />
            )}
        </>
    );
}


export interface BeltRadarTableButtonsProps {
    cell: CellContext<Session, unknown>;
    setSession: (session: Session) => void;
    setModalAction: (action: string | null) => void;
}

export function BeltRadarTableButtons({ cell, setSession, setModalAction }: BeltRadarTableButtonsProps) {
    return (
        <EntityTableActions
            cell={cell}
            onSelectEntity={setSession}
            setModalAction={setModalAction}
        />
    );
}

export interface BeltTimerTableButtonsProps {
    cell: CellContext<BeltTimer, unknown>;
    setTimer: (timer: BeltTimer) => void;
    setModalAction: (action: string | null) => void;
}

export function BeltTimerTableButtons({ cell, setTimer, setModalAction }: BeltTimerTableButtonsProps) {
    return (
        <EntityTableActions
            cell={cell}
            onSelectEntity={setTimer}
            setModalAction={setModalAction}
            showViewSession={Boolean(cell.row.original.has_session)}
        />
    );
}

