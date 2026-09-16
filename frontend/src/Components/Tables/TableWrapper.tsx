// Third Party
import { type ColumnDef } from "@tanstack/react-table";

// AA Belt Radar
import BaseTable from "@/Components/Tables/BaseTable";

const TableWrapper = <TData,>({
  data,
  isFetching,
  isError,
  columns,
}: {
  data?: TData[];
  isFetching: boolean;
  isError: boolean;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  columns: ColumnDef<TData, any>[];
}) => {
  return <BaseTable {...{ isFetching, isError, columns, data }} />;
};

export default TableWrapper;
