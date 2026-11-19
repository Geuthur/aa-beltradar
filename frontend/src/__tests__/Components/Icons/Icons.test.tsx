// Third Party
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

// AA Belt Radar
import { IconButton } from "@/Components/Icons/Icons";
import { SnapshotButtons } from "@/Components/Tables/Snapshot/SnapshotButtons";

describe("IconButton", () => {
  it("renders a small bootstrap button with the color variant and calls onClick", async () => {
    const onClick = vi.fn();
    render(<IconButton icon={<span>i</span>} title="Do it" color="danger" onClick={onClick} />);

    const button = screen.getByRole("button", { name: "Do it" });
    expect(button).toHaveClass("btn", "btn-sm", "btn-danger");

    await userEvent.click(button);
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});

describe("SnapshotButtons", () => {
  it("renders nothing without actions", () => {
    const { container } = render(
      <SnapshotButtons onAddClick={vi.fn()} onDeleteClick={vi.fn()} />,
    );
    expect(container).toBeEmptyDOMElement();
  });

  it("groups the action buttons in a ButtonGroup", () => {
    const { container } = render(
      <SnapshotButtons
        addAction={{ modal_id: "snapshot-add", url: "/a" } as never}
        deleteAction={{ modal_id: "snapshot-delete", url: "/d" } as never}
        onAddClick={vi.fn()}
        onDeleteClick={vi.fn()}
      />,
    );
    const group = container.querySelector(".btn-group.btn-group-sm");
    expect(group).not.toBeNull();
    expect(group?.querySelectorAll("button")).toHaveLength(2);
  });
});
