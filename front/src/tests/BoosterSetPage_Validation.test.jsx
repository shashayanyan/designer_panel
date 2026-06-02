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

describe("BoosterSetPage - Validation and Resets", () => {
  const mockSeries = [{ series_id: "VSD", name: "VSD" }];
  const mockStarters = [
    { series_id: "VSD", rated_load_power_kw: 15, starter_option_id: "OPT-1" },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("dashboard_token", "mock-token");
    fetch.mockImplementation((url) => {
      if (url.includes("/images/") || /\.(jpg|png)$/i.test(url)) {
        return Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(new Blob([""], { type: "image/png" })),
        });
      }
      if (url.includes("/api/v1/series")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockSeries),
        });
      }
      if (url.includes("/api/v1/starter-options")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockStarters),
        });
      }
      if (url.includes("/api/v1/enclosure-options/")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve([
              {
                reference: "ENC-1",
                material: "Aluminum",
                recommendation_type: "Recommended",
              },
            ]),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
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

  it("disables download button until all fields are filled", async () => {
    await renderComponent();

    const downloadBtn = screen.getByRole("button", {
      name: /Download Package/i,
    });
    expect(downloadBtn).toBeDisabled();

    // Fill partially
    fireEvent.change(screen.getByLabelText(/Number of Pumps/i), {
      target: { value: "3" },
    });
    expect(downloadBtn).toBeDisabled();

    // Fill everything
    fireEvent.change(screen.getByLabelText(/Type of Motor Start/i), {
      target: { value: "VSD" },
    });
    await waitFor(() =>
      expect(screen.getByLabelText(/Motor Power Rate/i)).not.toBeDisabled(),
    );
    fireEvent.change(screen.getByLabelText(/Motor Power Rate/i), {
      target: { value: "15" },
    });

    await waitFor(() =>
      expect(screen.getByLabelText(/Enclosure Type/i)).not.toBeDisabled(),
    );
    fireEvent.change(screen.getByLabelText(/Enclosure Type/i), {
      target: { value: "ENC-1" },
    });

    fireEvent.change(screen.getByLabelText(/Communication/i), {
      target: { value: "ModbusTCP" },
    });
    fireEvent.change(screen.getByLabelText(/SCADA/i), {
      target: { value: "No" },
    });
    fireEvent.change(screen.getByLabelText(/PLC/i), {
      target: { value: "No" },
    });

    expect(downloadBtn).not.toBeDisabled();
  });

  it("resets configuration and assets when Reset is clicked", async () => {
    await renderComponent();

    const pumpsSelect = screen.getByLabelText(/Number of Pumps/i);
    fireEvent.change(pumpsSelect, { target: { value: "3" } });

    const assetCheckbox = screen.getByLabelText("Multi Line Diagram");
    fireEvent.click(assetCheckbox);
    expect(assetCheckbox.checked).toBe(true);

    const resetBtn = screen.getByText("Reset");
    fireEvent.click(resetBtn);

    await waitFor(() => {
      expect(screen.getByLabelText(/Number of Pumps/i).value).toBe("");
      expect(screen.getByLabelText("Multi Line Diagram").checked).toBe(false);
    });
  });

  it("gracefully handles master data API failure", async () => {
    fetch.mockImplementation(() => Promise.reject("API Down"));

    // We expect console.error to be called
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    await renderComponent();

    const startTypeSelect = screen.getByLabelText(/Type of Motor Start/i);
    expect(startTypeSelect).toBeDisabled();
    expect(screen.getAllByText("Pending...").length).toBeGreaterThan(0);

    consoleSpy.mockRestore();
  });
});
