// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { NuqsTestingAdapter } from "nuqs/adapters/testing";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Belt Radar
import { apiClient } from "@/Api/Api";
import { ActionSectionHeader } from "@/Components/Base/ActionSectionHeader";

const renderHeader = (props: Partial<Parameters<typeof ActionSectionHeader>[0]> = {}) =>
  render(
    <NuqsTestingAdapter>
      <QueryClientProvider client={new QueryClient()}>
        <ActionSectionHeader name="Sessions" {...props}>
          <span>form</span>
        </ActionSectionHeader>
      </QueryClientProvider>
    </NuqsTestingAdapter>,
  );

describe("ActionSectionHeader", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("should show the button for a modal key without loading the menu", () => {
    // Test Data
    const get = vi.spyOn(apiClient, "GET");

    // Test Action
    renderHeader({ modalKey: "create_session", buttonTitle: "New Session" });

    // Expected Result
    expect(screen.getByRole("heading", { name: "Sessions" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New Session" })).toBeInTheDocument();
    expect(get).not.toHaveBeenCalled();
  });

  it("should show no button without a modal key", () => {
    // Test Action
    renderHeader();

    // Expected Result
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
  });

  it("should open the modal of the key on click", async () => {
    // Test Data
    renderHeader({ modalKey: "create_belt_timer", buttonTitle: "New Timer" });

    // Test Action
    await userEvent.click(screen.getByRole("button", { name: "New Timer" }));

    // Expected Result
    expect(await screen.findByText("Create Belt Timer")).toBeInTheDocument();
    expect(screen.getByText("form")).toBeInTheDocument();
  });
});
