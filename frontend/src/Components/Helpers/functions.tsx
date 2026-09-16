// Third Party
import type {
  Header,
  HeaderGroup,
  Table as ReactTable,
} from "@tanstack/react-table";
import { stringify } from "csv-stringify/browser/esm/sync";
import { OverlayTrigger } from "react-bootstrap";
import Tooltip from "react-bootstrap/esm/Tooltip";

/**
 * Helper functions for formatting dates and rendering HTML safely in React components
 * @param value The date string to format (optional)
 * @param options Optional Intl.DateTimeFormatOptions for customizing the output
 * @returns A formatted date string or "N/A" if the value is not provided
 */
export function formatDate(value?: string | null, options?: Intl.DateTimeFormatOptions): string {
  // Return "N/A" if the value is not provided
  if (!value) {
    return "N/A";
  }
	const locale = document.documentElement.lang || undefined;
	const hasExplicitTimeFields =
		options && (
			"hour" in options ||
			"minute" in options ||
			"second" in options ||
			"timeStyle" in options
		);
	const hasExplicitDateFields =
		options && (
			"year" in options ||
			"month" in options ||
			"day" in options ||
			"dateStyle" in options
		);

	const formatterOptions: Intl.DateTimeFormatOptions = {
		...(hasExplicitTimeFields || hasExplicitDateFields ? {} : { dateStyle: 'medium', timeStyle: 'short' }),
		...(options ?? {}),
	};

	return new Intl.DateTimeFormat(locale, formatterOptions).format(new Date(value));
}

/**
 * Helper function for rendering pre-rendered HTML safely in React components
 * @param value The HTML string to render
 */
export function renderHtml(value: string) {
	return <span dangerouslySetInnerHTML={{ __html: value }} />
}

// Internationalization helper for translating messages
export const gettext = (msg: string): string => msg;

/**
 * Helper function for rendering tooltips in a fixed position
 * @param message The message to display inside the tooltip
 * @param children The React element that triggers the tooltip
 */
export function renderTooltip(
  message: string,
  children: React.ComponentProps<typeof OverlayTrigger>["children"],
) {
  return (
    <OverlayTrigger
      trigger={["hover", "focus"]}
      overlay={
        <Tooltip id="aa-beltradar-tooltip" style={{ position: "fixed" }}>
          {message}
        </Tooltip>
      }
    >
      {children}
    </OverlayTrigger>
  );
}

/**
 * Helper function for exporting table data to CSV
 * @param table The React Table instance containing the data
 * @param exportFileName Optional file name for the exported CSV
 */
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
