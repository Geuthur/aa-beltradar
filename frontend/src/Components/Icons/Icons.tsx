// React
import { useNavigate } from "react-router-dom";

// Third Party
import type { CellContext } from "@tanstack/react-table";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import type { BeltTimer, Session } from "@/Api/schema";
import { renderTooltip } from "@/Components/Tables/BaseTable/tableHelper";

export interface ButtonProps {
	icon: string;
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
                <Button
                    onClick={onClick}
                    title={title}
                    size="sm"
                    variant={color}
                    className={`me-2 ${classProps ?? ""}`}>
                    <i className={icon}></i>
                </Button>
            )}
        </>
    );
}

export interface EntityWithActions {
    public_id: string;
    has_session?: boolean;
    actions?: {
        update?: {
            icon: string;
            title: string;
            color?: string | null;
            modal_id: string;
        } | null;
        delete?: {
            icon: string;
            title: string;
            color?: string | null;
            modal_id: string;
        } | null;
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
                    icon="fas fa-eye"
                    onClick={() => {
                        navigate("/beltradar/session/" + row.public_id + "/");
                    }}
                    title={t("View Session")}
                    color="primary"
                />
            )}
            {updateAction && (
                <IconButton
                    icon={updateAction.icon}
                    onClick={() => {
                        onSelectEntity?.(row);
                        setModalAction(updateAction.modal_id, row);
                    }}
                    title={updateAction.title}
                    color={updateAction.color ?? "success"}
                />
            )}
            {deleteAction && (
                <IconButton
                    icon={deleteAction.icon}
                    onClick={() => {
                        onSelectEntity?.(row);
                        setModalAction(deleteAction.modal_id, row);
                    }}
                    title={deleteAction.title}
                    color={deleteAction.color ?? "danger"}
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

