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

    // Expand to verify children
    fireEvent.click(screen.getByLabelText(/Expand Data Sheet/i));

    const children = ["Parameters", "BOM", "IO List", "Alarm List"];
    children.forEach((label) => {
      expect(screen.getByLabelText(label).checked).toBe(true);
    });
  });

  it("sets parent to indeterminate when some children are selected", async () => {
    await renderComponent();

    // Expand group
    fireEvent.click(screen.getByLabelText(/Expand Data Sheet/i));

    const parentCheckbox = screen.getByLabelText("Data Sheet");
    const childCheckbox = screen.getByLabelText("BOM");

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
    const otherChildren = ["Parameters", "IO List", "Alarm List", "Event List"];
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
    expect(screen.getByLabelText("Multi Line Diagram").checked).toBe(true);

    // Clear All
    fireEvent.click(clearAllBtn);

    expect(screen.getByLabelText("Data Sheet").checked).toBe(false);
    expect(screen.getByLabelText("Multi Line Diagram").checked).toBe(false);
  });
});
