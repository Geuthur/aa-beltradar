// React
import { MemoryRouter } from "react-router";

// Third Party
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

// AA Belt Radar
import BaseTable from "@/Components/Base/BaseTable/BaseTable";
import { createBaseColumnHelper } from "@/Components/Base/BaseTable/tableFeatures";

interface TestRow {
  id: number;
  name: string;
  role: string;
}

const columnHelper = createBaseColumnHelper<TestRow>();

const testColumns = [
  columnHelper.accessor("name", { header: "Name" }),
  columnHelper.accessor("role", { header: "Role" }),
];

const testData: TestRow[] = [
  { id: 1, name: "Alice", role: "admin" },
  { id: 2, name: "Bob", role: "user" },
  { id: 3, name: "Carol", role: "user" },
];

describe("BaseTable", () => {
  it("test_filter_should_hide_rows_not_matching_the_text_filter", async () => {
    // Test Data
    const user = userEvent.setup();
    const { container } = render(
      <MemoryRouter>
        <BaseTable data={testData} columns={testColumns} variant="bootstrap" />
      </MemoryRouter>,
    );
    const nameFilter = container.querySelectorAll("thead input")[0] as HTMLInputElement;

    // Test Action
    await user.type(nameFilter, "bo");

    // Expected Result: only Bob's row is left (check the body cells, not the whole page)
    const names = Array.from(container.querySelectorAll("tbody tr td:first-child")).map(
      (cell) => cell.textContent,
    );
    expect(names).toEqual(["Bob"]);
  });

  it("test_pagination_should_apply_initial_page_size", () => {
    // Test Data & Test Action
    const { container } = render(
      <MemoryRouter>
        <BaseTable
          data={testData}
          columns={testColumns}
          variant="bootstrap"
          initialState={{ pagination: { pageSize: 2 } }}
        />
      </MemoryRouter>,
    );

    // Expected Result
    expect(container.querySelectorAll("tbody tr").length).toBe(2);
  });
});
