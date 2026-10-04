// React
import { MemoryRouter } from "react-router-dom";

// Third Party
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

// AA Belt Radar
import * as BeltRadarApi from "@/Api/BeltRadar";
import { SettingsPage } from "@/Pages/SettingsPage";

vi.mock("@/Api/BeltRadar", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/Api/BeltRadar")>();
  return {
    ...actual,
    loadUserData: vi.fn(),
    updateUserSettings: vi.fn(),
  };
});

const renderPage = () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/beltradar/settings/"]}>
        <SettingsPage />
      </MemoryRouter>
    </QueryClientProvider>,
  );
};

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should load the saved global notification preference", async () => {
    // Test Data
    vi.mocked(BeltRadarApi.loadUserData).mockResolvedValueOnce({
      user: {
        user_id: 1,
        character_id: 12345,
        character_name: "Test Pilot",
        notification: true,
      },
    });

    // Test Action
    renderPage();

    // Expected Result
    expect(
      await screen.findByRole("switch", { name: "Disable all notifications" }),
    ).toBeChecked();
  });

  it("should save the global preference when the switch is enabled", async () => {
    // Test Data
    const user = userEvent.setup();
    vi.mocked(BeltRadarApi.loadUserData).mockResolvedValue({
      user: {
        user_id: 1,
        character_id: 12345,
        character_name: "Test Pilot",
        notification: false,
      },
    });
    vi.mocked(BeltRadarApi.updateUserSettings).mockResolvedValue({
      success: true,
    });

    // Test Action
    renderPage();
    const toggle = await screen.findByRole("switch", {
      name: "Disable all notifications",
    });
    await user.click(toggle);

    // Expected Result
    expect(BeltRadarApi.updateUserSettings).toHaveBeenCalledWith({
      disable_notifications: true,
    });
    await waitFor(() => expect(toggle).toBeChecked());
  });
});
