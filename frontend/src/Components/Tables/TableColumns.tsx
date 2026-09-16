// Third Party
import { createColumnHelper } from "@tanstack/react-table";
import type { ColumnDef } from "@tanstack/react-table";
import type { TFunction } from "i18next";

// AA Belt Radar
import { formatDate, renderHtml } from "@/Components/Helpers/functions";
import { EntityTableActions } from "@/Components/Icons/Icons";
import type { BeltTimer, Session, OreSchema } from "@/Api/schema";

export function getSessionColumns(
    t: TFunction,
    onSelectSession: (session: Session) => void,
    setModalAction: (action: string | null, session?: Session) => void,
): ColumnDef<Session, unknown>[] {
    const columnHelper = createColumnHelper<Session>();

    return [
        columnHelper.accessor("public_id", {
            header: t("Public ID"),
        }),
        columnHelper.accessor("name", {
            header: t("Name"),
        }),
        columnHelper.accessor("created_at", {
            header: t("Created At"),
            cell: ({ getValue }) => formatDate(getValue()),
        }),
        columnHelper.accessor("owner.portrait", {
            header: t("Owner"),
            cell: ({ getValue }) => renderHtml((getValue() as string) || "-"),
        }),
        columnHelper.accessor("public.display", {
            header: t("Public"),
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("actions", {
            header: t("Actions"),
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: (cell) => (
                <EntityTableActions
                    cell={cell}
                    onSelectEntity={onSelectSession}
                    setModalAction={setModalAction}
                />
            ),
        }),
    ] as ColumnDef<Session, unknown>[];
}

export function getBeltTimerColumns(
    t: TFunction,
    onSelectTimer: (timer: BeltTimer) => void,
    setModalAction: (action: string | null, timer?: BeltTimer) => void,
): ColumnDef<BeltTimer, unknown>[] {
    const columnHelper = createColumnHelper<BeltTimer>();

    return [
        columnHelper.accessor("public_id", {
            header: t("Public ID"),
        }),
        columnHelper.accessor("belt_name", {
            header: t("Belt Name"),
        }),
        columnHelper.accessor("belt_size", {
            header: t("Belt Size"),
        }),
        columnHelper.accessor("belt_type", {
            header: t("Belt Type"),
        }),
        columnHelper.accessor("eta.display", {
            header: t("ETA"),
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("public.display", {
            header: t("Public"),
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("actions", {
            header: t("Actions"),
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: (cell) => (
                <EntityTableActions
                    cell={cell}
                    onSelectEntity={onSelectTimer}
                    setModalAction={setModalAction}
                />
            ),
        }),
    ] as ColumnDef<BeltTimer, unknown>[];
}

export function getSnapshotColumns(
    t: TFunction,
): ColumnDef<OreSchema, unknown>[] {
    const columnHelper = createColumnHelper<OreSchema>();

    return [
		columnHelper.accessor('name', {
			header: t("Ore"),
		}),
		columnHelper.accessor('units', {
			header: t("Units Left"),
		}),
		columnHelper.accessor('volume_m3', {
			header: t("Volume Left (m³)"),
		}),
		columnHelper.accessor('price_isk', {
			header: t("Price (ISK/m³)"),
		}),
		columnHelper.accessor('price_compressed', {
			header: t("Price Compressed"),
		}),
		columnHelper.accessor('income_cmp_per_h', {
			header: t("Income Compressed (ISK/h)"),
		}),
    ] as ColumnDef<OreSchema, unknown>[];
}
