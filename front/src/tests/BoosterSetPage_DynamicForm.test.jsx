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

describe("BoosterSetPage - Dynamic Form Logic", () => {
  const mockSeries = [
    { series_id: "VSD", name: "Variable Speed Drive" },
    { series_id: "DOL", name: "Direct On Line" },
  ];
  const mockStarters = [
    {
      series_id: "VSD",
      rated_load_power_kw: 15,
      starter_option_id: "OPT-VSD-15",
    },
    {
      series_id: "VSD",
      rated_load_power_kw: 30,
      starter_option_id: "OPT-VSD-30",
    },
    {
      series_id: "DOL",
      rated_load_power_kw: 5.5,
      starter_option_id: "OPT-DOL-5.5",
    },
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
                reference: "ENC-REC",
                material: "Polyester",
                recommendation_type: "Recommended",
              },
              {
                reference: "ENC-ALT",
                material: "Steel",
                recommendation_type: "Alternative",
              },
            ]),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve({}) });
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

  it("updates motor power options based on selected motor start type", async () => {
    await renderComponent();

    const startTypeSelect = screen.getByLabelText(/Type of Motor Start/i);
    const powerSelect = screen.getByLabelText(/Motor Power Rate/i);

    // 1. Select VSD
    fireEvent.change(startTypeSelect, { target: { value: "VSD" } });

    await waitFor(() => {
      const options = Array.from(powerSelect.options).map((o) => o.value);
      expect(options).toContain("15");
      expect(options).toContain("30");
      expect(options).not.toContain("5.5");
    });

    // 2. Select DOL
    fireEvent.change(startTypeSelect, { target: { value: "DOL" } });

    await waitFor(() => {
      const options = Array.from(powerSelect.options).map((o) => o.value);
      expect(options).toContain("5.5");
      expect(options).not.toContain("15");
    });
  });

  it("fetches enclosure options when configuration is complete", async () => {
    await renderComponent();

    fireEvent.change(screen.getByLabelText(/Number of Pumps/i), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText(/Type of Motor Start/i), {
      target: { value: "VSD" },
    });

    await waitFor(() =>
      expect(screen.getByLabelText(/Motor Power Rate/i)).not.toBeDisabled(),
    );
    fireEvent.change(screen.getByLabelText(/Motor Power Rate/i), {
      target: { value: "15" },
    });

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining("/api/v1/enclosure-options/3/VSD/15"),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer mock-token",
          }),
        }),
      );
    });

    await waitFor(() => {
      const enclosureSelect = screen.getByLabelText(/Enclosure Type/i);
      const options = Array.from(enclosureSelect.options).map((o) => o.value);
      expect(options).toContain("ENC-REC");
      expect(options).toContain("ENC-ALT");
    });
  });

  it("handles enclosure fetch race conditions correctly", async () => {
    let callCount = 0;
    fetch.mockImplementation((url) => {
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
        callCount++;
        const currentCall = callCount;
        return new Promise((resolve) => {
          // Second call returns faster than first call
          const delay = currentCall === 1 ? 200 : 50;
          const result =
            currentCall === 1
              ? [
                  {
                    reference: "STALE-ENC",
                    material: "Polyester",
                    recommendation_type: "Recommended",
                  },
                ]
              : [
                  {
                    reference: "FRESH-ENC",
                    material: "Steel",
                    recommendation_type: "Recommended",
                  },
                ];

          setTimeout(() => {
            resolve({ ok: true, json: () => Promise.resolve(result) });
          }, delay);
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });

    await renderComponent();

    const pumpsSelect = screen.getByLabelText(/Number of Pumps/i);
    fireEvent.change(screen.getByLabelText(/Type of Motor Start/i), {
      target: { value: "VSD" },
    });
    await waitFor(() =>
      expect(screen.getByLabelText(/Motor Power Rate/i)).not.toBeDisabled(),
    );
    fireEvent.change(screen.getByLabelText(/Motor Power Rate/i), {
      target: { value: "15" },
    });

    // Rapidly change pumps
    fireEvent.change(pumpsSelect, { target: { value: "2" } }); // Call 1 (Stale, 200ms)
    fireEvent.change(pumpsSelect, { target: { value: "4" } }); // Call 2 (Fresh, 50ms)

    // Wait for the "Fresh" one to arrive (50ms)
    await waitFor(() => {
      const enclosureSelect = screen.getByLabelText(/Enclosure Type/i);
      const options = Array.from(enclosureSelect.options).map((o) => o.value);
      if (options.includes("FRESH-ENC")) return true;
      throw new Error("Fresh not yet arrived");
    });

    // Wait more to ensure "Stale" doesn't overwrite it
    await new Promise((r) => setTimeout(r, 300));

    const enclosureSelect = screen.getByLabelText(/Enclosure Type/i);
    const options = Array.from(enclosureSelect.options).map((o) => o.value);
    expect(options).toContain("FRESH-ENC");
    expect(options).not.toContain("STALE-ENC");
  });
});
