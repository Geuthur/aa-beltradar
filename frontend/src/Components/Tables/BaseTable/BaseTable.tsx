// React
import { useLocation } from "react-router";

// Third Party
import {
  flexRender,
  getCoreRowModel,
  getFacetedMinMaxValues,
  getFacetedRowModel,
  getFacetedUniqueValues,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import type {
  Cell,
  ColumnDef,
  InitialTableState,
} from "@tanstack/react-table";
import { Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import BaseHeader from "@/Components/Tables/BaseTable/BaseTableHeader";
import BasePages from "@/Components/Tables/BaseTable/BaseTablePages";

const isNumber = <TData,>(cell: Cell<TData, unknown>) => typeof cell.getValue() === "number";

export interface BaseTableProps<TData> {
  isFetching?: boolean;
  isError?: boolean;
  debugTable?: boolean;
  striped?: boolean;
  hover?: boolean;
  data?: TData[];
  columns: ColumnDef<TData, unknown>[];
  initialState?: InitialTableState;
  exportFileName?: string;
}

const BaseTable = <TData,>({
  isFetching = false,
  isError = false,
  debugTable = false,
  data = [],
  columns,
  striped = false,
  hover = false,
  initialState = undefined,
  exportFileName = undefined,
}: BaseTableProps<TData>) => {
  const location = useLocation();
  const { t } = useTranslation();

  // TanStack Table's useReactTable() returns functions the compiler can't
  // safely memoize; this is inherent to the library, not fixable here.
  // eslint-disable-next-line react-hooks/incompatible-library
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getFacetedRowModel: getFacetedRowModel(),
    getFacetedUniqueValues: getFacetedUniqueValues(),
    getFacetedMinMaxValues: getFacetedMinMaxValues(),
    debugTable,
    initialState: {
      pagination: { pageSize: 15 },
      ...initialState,
    },
  });

  const { rows } = table.getRowModel();
  const fileName =
    exportFileName !== undefined ? exportFileName : `ExportedData_${location.pathname}`;

  return (
    <>
      <Table {...{ striped, hover }}>
        <thead>
          <BaseHeader table={table} />
        </thead>
        <tbody>
          {isError ? (
            <tr>
              <td className="text-center" colSpan={table.getVisibleLeafColumns().length}>
                {t("No Data Available")}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <td
                    key={cell.id}
                    style={{
                      verticalAlign: "middle",
                      textAlign: isNumber(cell) ? "right" : "left",
                    }}
                  >
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </Table>
      <BasePages table={table} isFetching={isFetching} fileName={fileName} />
      {debugTable && (
        <div className="col-xs-12">
          <div>{t("{{count}} Rows", { count: table.getRowModel().rows.length })}</div>
          <pre>{JSON.stringify(table.getState(), null, 2)}</pre>
        </div>
      )}
    </>
  );
};

export default BaseTable;
