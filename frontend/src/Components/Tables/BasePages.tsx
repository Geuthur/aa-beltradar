// Third Party
import type { Table as TanStackTable } from "@tanstack/react-table";
import {
  Button,
  ButtonGroup,
  ButtonToolbar,
  Form,
  OverlayTrigger,
} from "react-bootstrap";
import { useTranslation } from "react-i18next";

// AA Belt Radar
import { exportToCSV, renderTooltip } from "../Helpers/functions";

// Styles
import tableStyles from "./BaseTable.module.css";

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
      <ButtonGroup style={{ zIndex: 0 }}>
        <Button active variant="info">
          {table.getState().pagination.pageIndex + 1} of {pageCount}
        </Button>
        {isFetching ? (
          <OverlayTrigger
            placement="bottom"
            trigger={["hover", "focus"]}
            overlay={renderTooltip(t("Refreshing Data"))}
          >
            <Button variant="info">
              <i className={`${tableStyles.refreshanimate} fas fa-sync`}></i>
            </Button>
          </OverlayTrigger>
        ) : (
          <OverlayTrigger
            placement="bottom"
            trigger={["hover", "focus"]}
            overlay={renderTooltip(
              t("Data Loaded: {{date}}", { date: new Date().toLocaleString() })
            )}
          >
            <Button variant="info">
              <i className="far fa-check-circle"></i>
            </Button>
          </OverlayTrigger>
        )}
        <Button
          variant="primary"
          onClick={() => exportToCSV(table, fileName ?? "ExportedData.csv")}
        >
          {t("Export Table to CSV")}
        </Button>
      </ButtonGroup>

      <ButtonToolbar>
        <ButtonGroup style={{ zIndex: 0 }}>
          <Button
            variant="success"
            onClick={() => table.setPageIndex(0)}
            disabled={!table.getCanPreviousPage()}
          >
            <i className="fas fa-angle-double-left"></i>
          </Button>
          <Button
            variant="success"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            <i className="fas fa-caret-left"></i>
          </Button>
          <Button
            variant="success"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            <i className="fas fa-caret-right"></i>
          </Button>
          <Button
            variant="success"
            onClick={() => table.setPageIndex(table.getPageCount() - 1)}
            disabled={!table.getCanNextPage()}
          >
            <i className="fas fa-angle-double-right"></i>
          </Button>
        </ButtonGroup>

        <div className="d-flex align-items-center ms-2">
          <Form.Label className="m-0 me-2 text-nowrap">{t("Page Size:")}</Form.Label>
          <Form.Select
            style={{ width: "auto" }}
            value={table.getState().pagination.pageSize}
            onChange={(e) => table.setPageSize(Number(e.target.value))}
          >
            {[15, 30, 60, 100, 1000000].map((_pageSize) => (
              <option key={_pageSize} value={_pageSize}>
                {_pageSize === 1000000
                  ? t("Show All")
                  : t("Show {{pageSize}}", { pageSize: _pageSize })}
              </option>
            ))}
          </Form.Select>
        </div>
      </ButtonToolbar>
    </div>
  );
};

export default BasePages;
