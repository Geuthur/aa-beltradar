// Third Party
import { createColumnHelper } from "@tanstack/react-table";
import type { ColumnDef } from "@tanstack/react-table";
import type { TFunction } from "i18next";

// AA Belt Radar
import type { BeltTimer, Session, OreSchema } from "@/Api/schema";
import { EntityTableActions } from "@/Components/Icons/Icons";
import { formatDate, formatNumber, renderHtml } from "@/Components/Tables/BaseTable/tableHelper";

export function getSessionColumns(
    t: TFunction,
    onSelectSession: (session: Session) => void,
    setModalAction: (action: string | null, session?: Session) => void,
): ColumnDef<Session, unknown>[] {
    const columnHelper = createColumnHelper<Session>();

    // Translations for tooltips and titles
    const tPublicID = t("Public ID");
    const tName = t("Name");
    const tCreatedAt = t("Created At");
    const tOwner = t("Owner");
    const tPublic = t("Public");
    const tActions = t("Actions");

    return [
        columnHelper.accessor("public_id", {
            header: tPublicID,
        }),
        columnHelper.accessor("name", {
            header: tName,
        }),
        columnHelper.accessor("created_at", {
            header: tCreatedAt,
            cell: ({ getValue }) => formatDate(getValue()),
        }),
        columnHelper.accessor("owner.portrait", {
            header: tOwner,
            cell: ({ getValue }) => renderHtml((getValue() as string) || "-"),
        }),
        columnHelper.accessor("public.display", {
            header: tPublic,
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("actions", {
            header: tActions,
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

    // Translations for tooltips and titles
    const tPublicID = t("Public ID");
    const tBeltName = t("Belt Name");
    const tBeltSize = t("Belt Size");
    const tBeltType = t("Belt Type");
    const tETA = t("ETA");
    const tPublic = t("Public");
    const tActions = t("Actions");

    return [
        columnHelper.accessor("public_id", {
            header: tPublicID,
        }),
        columnHelper.accessor("belt_name", {
            header: tBeltName,
        }),
        columnHelper.accessor("belt_size", {
            header: tBeltSize,
        }),
        columnHelper.accessor("belt_type", {
            header: tBeltType,
        }),
        columnHelper.accessor("eta.display", {
            header: tETA,
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("public.display", {
            header: tPublic,
            enableSorting: false,
            enableColumnFilter: false,
            enableGlobalFilter: false,
            cell: ({ getValue }) => renderHtml(getValue() as string),
        }),
        columnHelper.accessor("actions", {
            header: tActions,
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

    // Translations for tooltips and titles
    const tOre = t("Ore");
    const tUnitsLeft = t("Units Left");
    const tVolumeLeft = t("Volume Left (m³)");
    const tPriceISK = t("Price (ISK/m³)");
    const tPriceCompressed = t("Price Compressed");
    const tIncomeCompressed = t("Income Compressed (ISK/h)");

    return [
        columnHelper.accessor('name', {
            header: tOre,
        }),
        columnHelper.accessor('units', {
            header: tUnitsLeft,
            cell: ({ getValue }) => formatNumber(Number(getValue())),
        }),
        columnHelper.accessor('volume_m3', {
            header: tVolumeLeft,
            cell: ({ getValue }) => formatNumber(Number(getValue())),
        }),
        columnHelper.accessor('price_isk', {
            header: tPriceISK,
            cell: ({ getValue }) => formatNumber(Number(getValue())),
        }),
        columnHelper.accessor('price_compressed', {
            header: tPriceCompressed,
            cell: ({ getValue }) => formatNumber(Number(getValue())),
        }),
        columnHelper.accessor('income_cmp_per_h', {
            header: tIncomeCompressed,
            cell: ({ getValue }) => formatNumber(Number(getValue())),
        }),
    ] as ColumnDef<OreSchema, unknown>[];
}
