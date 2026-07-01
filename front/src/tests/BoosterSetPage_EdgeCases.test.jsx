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
import JSZip from "jszip";

// Mock navigate
const mockedNavigate = vi.fn();

// Mock URL methods
global.URL.createObjectURL = vi.fn(() => "mock-url");
global.URL.revokeObjectURL = vi.fn();

// Mock JSZip
vi.mock("jszip", () => {
  const mockZip = {
    file: vi.fn().mockReturnThis(),
    generateAsync: vi.fn().mockResolvedValue(new Blob(["mock-zip"])),
  };
  return {
    default: {
      loadAsync: vi.fn().mockResolvedValue(mockZip),
    },
  };
});

describe("BoosterSetPage - Edge Cases and SVG Logic", () => {
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
      return Promise.resolve({
        ok: true,
        blob: () => Promise.resolve(new Blob(["backend-zip"])),
      });
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

  const fillForm = async () => {
    fireEvent.change(screen.getByLabelText(/Number of Pumps/i), {
      target: { value: "2" },
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
  };

  it("handles failure of the generate-package API", async () => {
    await renderComponent();
    await fillForm();

    fetch.mockImplementation((url) => {
      if (url.includes("generate-package")) {
        return Promise.resolve({ ok: false });
      }
      if (url.includes("/images/") || /\.(jpg|png)$/i.test(url)) {
        return Promise.resolve({
          ok: true,
          blob: () => Promise.resolve(new Blob([""], { type: "image/png" })),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });

    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});

    fireEvent.click(screen.getByRole("button", { name: /Download Package/i }));

    await waitFor(() => {
      expect(alertSpy).toHaveBeenCalledWith(
        expect.stringContaining("Failed to generate package"),
      );
    });
    alertSpy.mockRestore();
  });

  it("processes images in ZIP if Multi Line Diagram is selected", async () => {
    await renderComponent();
    await fillForm();

    // Select Multi Line Diagram
    fireEvent.click(screen.getByLabelText("Electrical Multi Line Diagram"));

    const downloadBtn = screen.getByRole("button", {
      name: /Download Package/i,
    });

    await act(async () => {
      fireEvent.click(downloadBtn);
    });

    await waitFor(() => {
      expect(JSZip.loadAsync).toHaveBeenCalled();
    });
  });

  it("renders various SVG architectural paths based on control selection", async () => {
    await renderComponent();

    const scadaSelect = screen.getByLabelText(/SCADA/i);
    const plcSelect = screen.getByLabelText(/PLC/i);
    const commsSelect = screen.getByLabelText(/Communication/i);

    // 1. SCADA YES, PLC YES
    await act(async () => {
      fireEvent.change(scadaSelect, { target: { value: "YES" } });
      fireEvent.change(plcSelect, { target: { value: "YES" } });
    });
    // This should trigger hasSCADA && hasPLC path in SVG

    // 2. SCADA YES, PLC NO, Comms ModbusTCP
    await act(async () => {
      fireEvent.change(plcSelect, { target: { value: "No" } });
      fireEvent.change(commsSelect, { target: { value: "ModbusTCP" } });
    });
    // This should trigger hasSCADA && !hasPLC && hasComms path

    // 3. No SCADA, No PLC, Comms ModbusTCP
    await act(async () => {
      fireEvent.change(scadaSelect, { target: { value: "No" } });
    });
    // This should trigger !hasSCADA && !hasPLC && hasComms path

    // 4. Hardwired Case
    await act(async () => {
      fireEvent.change(commsSelect, { target: { value: "No" } });
      fireEvent.change(plcSelect, { target: { value: "YES" } });
    });

    expect(screen.getByText("Hardwired I/O Bus")).toBeInTheDocument();
  });

  it("handles catch block error in handleDownload", async () => {
    await renderComponent();
    await fillForm();

    fetch.mockImplementation((url) => {
      if (url.includes("generate-package")) {
        throw new Error("Network Error");
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });

    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    fireEvent.click(screen.getByRole("button", { name: /Download Package/i }));

    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith(
        "Error generating zip:",
        expect.any(Error),
      );
    });
    consoleSpy.mockRestore();
  });
});
