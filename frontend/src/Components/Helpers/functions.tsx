// Third Party
import type {
  Header,
  HeaderGroup,
  Table as ReactTable,
} from "@tanstack/react-table";
import { stringify } from "csv-stringify/browser/esm/sync";
import Tooltip from "react-bootstrap/esm/Tooltip";

// Helper functions for formatting dates and rendering HTML safely in React components
export function formatDate(value: string): string {
	return new Intl.DateTimeFormat(document.documentElement.lang || undefined, {
		dateStyle: 'medium',
		timeStyle: 'short',
	}).format(new Date(value))
}

// Backend returns pre-rendered HTML (e.g. character portraits, status badges) that must be injected, not escaped
export function renderHtml(value: string) {
	return <span dangerouslySetInnerHTML={{ __html: value }} />
}

// Internationalization helper for translating messages
export const gettext = (msg: string): string => msg;

// Tooltip helper for rendering messages in a fixed position

export function renderTooltip(message: string) {
  return (
	<Tooltip id="aa-beltradar-tooltip" style={{ position: "fixed" }}>
	  {message}
	</Tooltip>
  );
}

export const exportToCSV = <TData,>(table: ReactTable<TData>, exportFileName?: string) => {
  const { rows } = table.getFilteredRowModel();
  const safeFileName = exportFileName ?? "ExportedData.csv";

  const headerRows = table.getHeaderGroups().map((headerGroup: HeaderGroup<TData>) =>
    headerGroup.headers.map((header: Header<TData, unknown>) => {
      if (typeof header.column.columnDef.header === "function") {
        return (header.column.columnDef as { accessorKey?: string }).accessorKey;
      }
      return header.column.columnDef.header;
    }),
  );

  const csvData = rows.map((row) => row.getVisibleCells().map((cell) => cell.getValue()));

  const csv = stringify([...headerRows, ...csvData]);
  const blob = new Blob([csv], { type: "text/csv;charset=utf8;" });

  const link = document.createElement("a");
  link.download = safeFileName;
  link.href = URL.createObjectURL(blob);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
