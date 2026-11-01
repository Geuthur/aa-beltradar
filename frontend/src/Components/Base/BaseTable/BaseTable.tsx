// React
import { useLocation } from "react-router";

// Third Party
import { flexRender, useTable } from "@tanstack/react-table";
import type { Cell, Row, RowData, TableState } from "@tanstack/react-table";
import {
  ArrowUpDown,
  ChevronDown,
  ChevronFirst,
  ChevronLast,
  ChevronLeft,
  ChevronRight,
  ChevronUp,
} from "lucide-react";
import { Button, Form, Table } from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import BaseHeader from "@/Components/Base/BaseTable/BaseTableHeader";
import BasePages from "@/Components/Base/BaseTable/BaseTablePages";
import { baseTableFeatures } from "@/Components/Base/BaseTable/tableFeatures";
import type { BaseColumnDef, BaseTableFeatures } from "@/Components/Base/BaseTable/tableFeatures";
import styles from "@/Styles/modules/BaseTable.module.css";

// Like v8's InitialTableState: each slice may be given partially (e.g. only pageSize).
export type BaseTableInitialState = {
  [K in keyof TableState<BaseTableFeatures>]?: Partial<TableState<BaseTableFeatures>[K]>;
};

const isNumber = <TData extends RowData,>(cell: Cell<BaseTableFeatures, TData, unknown>) => typeof cell.getValue() === "number";

export interface BaseTableProps<TData extends RowData, TValue = unknown> {
  isFetching?: boolean;
  isError?: boolean;
  debugTable?: boolean;
  striped?: boolean;
  hover?: boolean;
  data?: TData[];
  columns: BaseColumnDef<TData, TValue>[];
  initialState?: BaseTableInitialState;
  exportFileName?: string;
  variant?: "bootstrap" | "aa";
  emptyText?: string;
  className?: string;
  tableClassName?: string;
  pageSizeOptions?: number[];
  itemLabel?: string;
  getRowClassName?: (row: Row<BaseTableFeatures, TData>) => string;
}

const BaseTable = <TData extends RowData, TValue = unknown>({
  isFetching = false,
  isError = false,
  debugTable = false,
  data = [],
  columns,
  striped = false,
  hover = false,
  initialState = undefined,
  exportFileName = undefined,
  variant = "aa",
  emptyText,
  className,
  tableClassName,
  pageSizeOptions = [10, 25, 50, 100],
  itemLabel,
  getRowClassName,
}: BaseTableProps<TData, TValue>) => {
  const location = useLocation();
  const { t } = useTranslation();

  const table = useTable({
    features: baseTableFeatures,
    data,
    columns,
    debugTable,
    initialState: {
      ...initialState,
      pagination: { pageIndex: 0, pageSize: 15, ...initialState?.pagination },
    } as Partial<TableState<BaseTableFeatures>>,
  });

  const { rows } = table.getRowModel();
  const fileName =
    exportFileName !== undefined ? exportFileName : `ExportedData_${location.pathname}`;

  if (variant === "aa") {
    const totalCount = table.getPrePaginatedRowModel().rows.length;
    const { pageIndex, pageSize } = table.state.pagination;
    const pageCount = table.getPageCount();

    return (
      <div
        className={`aa-table-shell ${className ?? ""}`}
      >
        <div className="aa-table-scroll">
          <table
            className={`aa-table ${tableClassName ?? ""}`}
          >
            <thead className="aa-table-head">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    const canSort = header.column.getCanSort();
                    const isSorted = header.column.getIsSorted();
                    return (
                      <th
                        key={header.id}
                        colSpan={header.colSpan}
                        onClick={canSort ? header.column.getToggleSortingHandler() : undefined}
                        className={`aa-table-heading-cell ${
                          canSort
                            ? "aa-table-sortable"
                            : ""
                        }`}
                      >
                        <div className="aa-table-heading">
                          {flexRender(header.column.columnDef.header, header.getContext())}
                          {canSort && (
                            <span>
                              {isSorted === "asc" ? (
                                <ChevronUp className="aa-table-sort-icon aa-table-sort-icon-active" />
                              ) : isSorted === "desc" ? (
                                <ChevronDown className="aa-table-sort-icon aa-table-sort-icon-active" />
                              ) : (
                                <ArrowUpDown className="aa-table-sort-icon" />
                              )}
                            </span>
                          )}
                        </div>
                      </th>
                    );
                  })}
                </tr>
              ))}
            </thead>
            <tbody className="aa-table-body">
              {isError ? (
                <tr>
                  <td
                    colSpan={table.getVisibleLeafColumns().length}
                    className="aa-table-message"
                  >
                    {t("Something went wrong.")}
                  </td>
                </tr>
              ) : rows.length === 0 ? (
                <tr>
                  <td
                    colSpan={table.getVisibleLeafColumns().length}
                    className="aa-table-message"
                  >
                    {emptyText ?? t("No Data Available")}
                  </td>
                </tr>
              ) : (
                rows.map((row) => (
                  <tr
                    key={row.id}
                    className={`aa-table-row ${
                      getRowClassName
                        ? getRowClassName(row)
                        : "aa-table-row-hover"
                    }`}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <td
                        key={cell.id}
                        className={`aa-table-cell ${styles["cell-middle"]}`}
                      >
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* DataTable Footer Controls */}
        <div className="aa-table-footer">
          {/* Page Size Selector & Count Indicator */}
          <div className="aa-table-controls">
            <div className="aa-table-page-size">
              <span>{t("Page Size:")}</span>
              <Form.Select
                size="sm"
                value={pageSize}
                onChange={(e) => table.setPageSize(Number(e.target.value))}
                className={`aa-table-select ${styles["page-size-select"]}`}
              >
                {pageSizeOptions.map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
                <option value={1000000}>{t("Show All")}</option>
              </Form.Select>
            </div>

            {totalCount > 0 && (
              <span className="aa-table-count">
                {pageSize >= 1000000
                  ? t("Showing all {{total}} {{items}}", {
                      total: totalCount,
                      items: itemLabel ?? t("entries"),
                    })
                  : t("Showing {{start}}-{{end}} of {{total}} {{items}}", {
                      start: pageIndex * pageSize + 1,
                      end: Math.min((pageIndex + 1) * pageSize, totalCount),
                      total: totalCount,
                      items: itemLabel ?? t("entries"),
                    })}
              </span>
            )}
          </div>

          {/* Pagination Buttons */}
          {pageCount > 1 && (
            <div className="aa-table-pagination">
              <Button
                size="sm"
                disabled={!table.getCanPreviousPage()}
                onClick={() => table.setPageIndex(0)}
                className="aa-table-page-button"
                title={t("First Page")}
              >
                <ChevronFirst className="aa-table-page-icon" />
              </Button>
              <Button
                size="sm"
                disabled={!table.getCanPreviousPage()}
                onClick={() => table.previousPage()}
                className="aa-table-page-button"
                title={t("Previous Page")}
              >
                <ChevronLeft className="aa-table-page-icon" />
              </Button>

              <span className="aa-table-page-number">
                {t("Page {{page}} of {{total}}", {
                  page: pageIndex + 1,
                  total: pageCount,
                })}
              </span>

              <Button
                size="sm"
                disabled={!table.getCanNextPage()}
                onClick={() => table.nextPage()}
                className="aa-table-page-button"
                title={t("Next Page")}
              >
                <ChevronRight className="aa-table-page-icon" />
              </Button>
              <Button
                size="sm"
                disabled={!table.getCanNextPage()}
                onClick={() => table.setPageIndex(pageCount - 1)}
                className="aa-table-page-button"
                title={t("Last Page")}
              >
                <ChevronLast className="aa-table-page-icon" />
              </Button>
            </div>
          )}
        </div>
      </div>
    );
  }

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
                    className={`${styles["cell-middle"]} ${isNumber(cell) ? styles["cell-right"] : styles["cell-left"]}`}
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
          <pre>{JSON.stringify(table.state, null, 2)}</pre>
        </div>
      )}
    </>
  );
};

export default BaseTable;
