import {
  render,
  screen,
  fireEvent,
  act,
  waitFor,
} from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, vi, beforeEach } from "vitest";
import BoosterSetPage from "../pages/BoosterSetPage";
import { AuthContext } from "../context/AuthContext";
import React from "react";

// Mock navigate
const mockedNavigate = vi.fn();

describe("BoosterSetPage - Asset Tree Logic", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("dashboard_token", "mock-token");
    fetch.mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([]),
    });
  });

  const renderComponent = async () => {
    await act(async () => {
      render(
        <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
          <BrowserRouter>
            <BoosterSetPage />
          </BrowserRouter>
        </AuthContext.Provider>,
      );
    });
  };

  it("cascades selection from parent to all children", async () => {
    await renderComponent();

    const parentCheckbox = screen.getByLabelText("Data Sheet");

    // Check parent
    fireEvent.click(parentCheckbox);
    expect(parentCheckbox.checked).toBe(true);

    // Expand to verify children if not already expanded
    const expandBtn1 = screen.queryByLabelText(/Expand Data Sheet/i);
    if (expandBtn1) {
      fireEvent.click(expandBtn1);
    }

    const children = [
      "System Parameters",
      "BOM - Bill of Materials",
      "List of Inputs/Outputs",
      "List of Alarms",
    ];
    children.forEach((label) => {
      expect(screen.getByLabelText(label).checked).toBe(true);
    });
  });

  it("sets parent to indeterminate when some children are selected", async () => {
    await renderComponent();

    // Expand group if not already expanded
    const expandBtn2 = screen.queryByLabelText(/Expand Data Sheet/i);
    if (expandBtn2) {
      fireEvent.click(expandBtn2);
    }

    const parentCheckbox = screen.getByLabelText("Data Sheet");
    const childCheckbox = screen.getByLabelText("BOM - Bill of Materials");

    // Initially none selected
    expect(parentCheckbox.checked).toBe(false);
    expect(parentCheckbox.indeterminate).toBe(false);

    // Select one child
    fireEvent.click(childCheckbox);

    expect(childCheckbox.checked).toBe(true);

    // Find parent checkbox specifically by role and name
    const parentInput = screen.getByRole("checkbox", { name: /Data Sheet/i });
    expect(parentInput.checked).toBe(false);

    await waitFor(() => expect(parentInput.indeterminate).toBe(true), {
      timeout: 2000,
    });
    // Select all other children to reach "all selected" state
    const otherChildren = [
      "System Parameters",
      "List of Inputs/Outputs",
      "List of Alarms",
      "List of Events",
    ];
    await act(async () => {
      for (const label of otherChildren) {
        fireEvent.click(screen.getByLabelText(label));
      }
    });

    await waitFor(
      () => {
        const liveParentInput = screen.getByRole("checkbox", {
          name: /Data Sheet/i,
        });
        expect(liveParentInput.checked).toBe(true);
        expect(liveParentInput.indeterminate).toBe(false);
      },
      { timeout: 2000 },
    );
  });

  it("handles Select All and Clear All global actions", async () => {
    await renderComponent();

    const selectAllBtn = screen.getByText("Select All");
    const clearAllBtn = screen.getByText("Clear All");

    // Select All
    fireEvent.click(selectAllBtn);

    expect(screen.getByLabelText("Data Sheet").checked).toBe(true);
    expect(screen.getByLabelText("Electrical Multi Line Diagram").checked).toBe(
      true,
    );

    // Clear All
    fireEvent.click(clearAllBtn);

    expect(screen.getByLabelText("Data Sheet").checked).toBe(false);
    expect(screen.getByLabelText("Electrical Multi Line Diagram").checked).toBe(
      false,
    );
  });
});
