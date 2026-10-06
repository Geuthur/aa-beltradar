// Third Party
import type { Table as TanStackTable } from "@tanstack/react-table";
import {
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  CircleCheck,
  RefreshCw,
} from "lucide-react";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
} from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { BaseTableForm } from "@/Components/Base/BaseTable/BaseTableForm";
import { exportToCSV, renderTooltip } from "@/Components/Base/BaseTable/tableHelper";
import tableStyles from "@/Styles/modules/BaseTable.module.css";
import pageStyles from "@/Styles/modules/BaseTablePages.module.css";

export interface TablePagesProps<TData> {
  table: TanStackTable<TData>;
  isFetching?: boolean;
  fileName?: string;
}

const BasePages = <TData,>({
  table,
  isFetching = false,
  fileName,
}: TablePagesProps<TData>) => {
  const { t } = useTranslation();
  const pageCount = Math.max(1, table.getPageCount());

  return (
    <div className="d-flex justify-content-between">
      <ButtonGroup className={pageStyles["button-group"]}>
        <Button active variant="info">
          {t("Page {{page}} of {{total}}", {
            page: table.getState().pagination.pageIndex + 1,
            total: pageCount,
          })}
        </Button>
        {isFetching ? (
          renderTooltip(
            t("Refreshing Data"),
            <Button variant="info">
              <RefreshCw className={tableStyles.refreshanimate} size={14} />
            </Button>
          )
        ) : (
          renderTooltip(
            t("Data Loaded: {{date}}", { date: new Date().toLocaleString() }),
            <Button variant="info">
              <CircleCheck size={14} />
            </Button>
          )
        )}
        <Button
          variant="primary"
          onClick={() => exportToCSV(table, fileName ?? "ExportedData.csv")}
        >
          {t("Export Table to CSV")}
        </Button>
      </ButtonGroup>

      <ButtonToolbar>
        <ButtonGroup className={pageStyles["button-group"]}>
          <Button
            variant="success"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronsLeft size={14} />
          </Button>
          <Button
            variant="success"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <ChevronLeft size={14} />
          </Button>
          <Button
            variant="success"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <ChevronRight size={14} />
          </Button>
          <Button
            variant="success"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <ChevronsRight size={14} />
          </Button>
        </ButtonGroup>

        <BaseTableForm table={table} />
      </ButtonToolbar>
    </div>
  );
};

export default BasePages;
