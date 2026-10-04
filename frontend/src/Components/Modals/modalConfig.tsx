// React
import type { ReactNode } from "react";

// Third Party
import type { TFunction } from "i18next";
import { CircleHelp, Plus, Trash2, Wrench } from "lucide-react";

export type ModalColor = "primary" | "secondary" | "success" | "warning" | "danger";

export interface ModalConfig {
  icon: ReactNode;
  title: string;
  /** Confirmation text shown in the modal body */
  text: string;
  color: ModalColor;
}

const icon = {
  add: <Plus size={14} aria-hidden="true" />,
  modify: <Wrench size={14} aria-hidden="true" />,
  delete: <Trash2 size={14} aria-hidden="true" />,
  unknown: <CircleHelp size={14} aria-hidden="true" />,
};

/** The API only sends the modal_id of an action; icon, title and texts are defined here. */
export function getModalConfig(t: TFunction, modalId: string): ModalConfig {
  switch (modalId) {
    case "beltradar-accept-create-session":
      return {
        icon: icon.add,
        color: "success",
        title: t("Create Session"),
        text: t("Are you sure you want to create a new session?"),
      };
    case "beltradar-accept-delete-session":
      return {
        icon: icon.delete,
        color: "danger",
        title: t("Delete Session"),
        text: t("Are you sure you want to delete this session?"),
      };
    case "beltradar-accept-modify-session":
      return {
        icon: icon.modify,
        color: "warning",
        title: t("Modify Session"),
        text: t("Are you sure you want to switch public/private status for this session?"),
      };
    case "beltradar-accept-create-belt-timer":
      return {
        icon: icon.add,
        color: "success",
        title: t("Create Belt Timer"),
        text: t("Are you sure you want to create a belt timer for this session?"),
      };
    case "beltradar-accept-modify-belt-timer":
      return {
        icon: icon.modify,
        color: "warning",
        title: t("Modify Belt Timer"),
        text: t("Modify Belt Timer"),
      };
    case "beltradar-accept-delete-belt-timer":
      return {
        icon: icon.delete,
        color: "danger",
        title: t("Delete Belt Timer"),
        text: t("Are you sure you want to delete this belt timer?"),
      };
    case "beltradar-add-snapshot":
      return {
        icon: icon.add,
        color: "success",
        title: t("Add Snapshot"),
        text: t("Add Snapshot"),
      };
    case "beltradar-accept-delete-snapshot":
      return {
        icon: icon.delete,
        color: "danger",
        title: t("Delete Snapshot"),
        text: t("Are you sure you want to delete this snapshot?"),
      };
    default:
      return { icon: icon.unknown, color: "primary", title: modalId, text: "" };
  }
}
