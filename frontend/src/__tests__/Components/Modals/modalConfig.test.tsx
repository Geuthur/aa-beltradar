// Third Party
import { renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";

// AA Belt Radar
import { sectionModals, useModalData } from "@/Components/Modals/modalConfig";

describe("sectionModals", () => {
  it("should keep the modal ids and the create endpoints", () => {
    // Expected Result
    expect(sectionModals).toEqual({
      create_session: {
        modal_id: "beltradar-accept-create-session",
        url: "/beltradar/api/manage/session/add/",
      },
      create_belt_timer: {
        modal_id: "beltradar-accept-create-belt-timer",
        url: "/beltradar/api/manage/belt-timer/create/",
      },
    });
  });
});

describe("useModalData", () => {
  it("should complete a section modal with title, text and color", () => {
    // Test Action
    const { result } = renderHook(() => useModalData(sectionModals.create_session));

    // Expected Result
    expect(result.current).toEqual({
      modal_id: "beltradar-accept-create-session",
      url: "/beltradar/api/manage/session/add/",
      title: "Create Session",
      text: "Are you sure you want to create a new session?",
      icon: "",
      color: "success",
    });
  });

  it("should return nothing without an action", () => {
    // Test Action
    const { result } = renderHook(() => useModalData(null));

    // Expected Result
    expect(result.current).toBeUndefined();
  });
});
