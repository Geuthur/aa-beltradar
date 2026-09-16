// React
import { useNavigate } from "react-router-dom";

// Third Party
import type { CellContext } from "@tanstack/react-table";
import { Button } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { renderTooltip } from "@/Components/Helpers/functions";
import type { BeltTimer, Session } from "@/Components/Props/BeltRadarProps";

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

export interface BeltRadarTableButtonsProps {
    cell: CellContext<Session, unknown>;
    setSession: (session: Session) => void;
    setModalAction: (action: string | null) => void;
}

export interface BeltTimerTableButtonsProps {
    cell: CellContext<BeltTimer, unknown>;
    setTimer: (timer: BeltTimer) => void;
    setModalAction: (action: string | null) => void;
}

export function BeltRadarTableButtons({ cell, setSession, setModalAction }: BeltRadarTableButtonsProps) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const row = cell.row.original;
    const updateAction = row.actions?.update;
    const deleteAction = row.actions?.delete;

    return (
        <>
            <IconButton
                icon="fas fa-eye"
                onClick={() => {
                    navigate("/beltradar/session/" + row.public_id + "/");
                }}
                title={t("View Session")}
                color="primary"
            />
            {updateAction && (
                <IconButton
                    icon={updateAction.icon}
                    onClick={() => {
                        setSession(row);
                        setModalAction(updateAction.modal_id);
                    }}
                    title={updateAction.title}
                    color={updateAction.color ?? "success"}
                />
            )}
            {deleteAction && (
                <IconButton
                    icon={deleteAction.icon}
                    onClick={() => {
                        setSession(row);
                        setModalAction(deleteAction.modal_id);
                    }}
                    title={deleteAction.title}
                    color={deleteAction.color ?? "danger"}
                />
            )}
        </>
    );
}

export function BeltTimerTableButtons({ cell, setTimer, setModalAction }: BeltTimerTableButtonsProps) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const row = cell.row.original;
    const updateAction = row.actions?.update;
    const deleteAction = row.actions?.delete;

    return (
        <>
            <IconButton
                icon="fas fa-eye"
                onClick={() => {
                    navigate("/beltradar/session/" + row.public_id + "/");
                }}
                title={t("View Session")}
                color="primary"
            />
            {updateAction && (
                <IconButton
                    icon={updateAction.icon}
                    onClick={() => {
                        setTimer(row);
                        setModalAction(updateAction.modal_id);
                    }}
                    title={updateAction.title}
                    color={updateAction.color ?? "success"}
                />
            )}
            {deleteAction && (
                <IconButton
                    icon={deleteAction.icon}
                    onClick={() => {
                        setTimer(row);
                        setModalAction(deleteAction.modal_id);
                    }}
                    title={deleteAction.title}
                    color={deleteAction.color ?? "danger"}
                />
            )}
        </>
    );
}
