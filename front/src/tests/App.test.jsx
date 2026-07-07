import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import App from "../App";
import React from "react";

describe("App Routing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();

    // Mock fetch to return 401 for auth by default, and empty arrays for others
    fetch.mockImplementation((url) => {
      if (url.includes("/me")) {
        return Promise.resolve({ ok: false, status: 401 });
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve([]),
        blob: () => Promise.resolve(new Blob()),
      });
    });
  });

  it("navigates through the application flow", async () => {
    // 1. Start at Login (because no token)
    await act(async () => {
      render(<App />);
    });
    expect(screen.getByText(/Sign in to Designer Panel/i)).toBeInTheDocument();

    // 2. Mock login
    fetch.mockImplementation((url) => {
      if (url.includes("/login")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: "mock-token" }),
        });
      }
      if (url.includes("/me")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ username: "testuser", role: "User" }),
        });
      }
      return Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
    });

    fireEvent.change(screen.getByPlaceholderText(/Username/i), {
      target: { value: "testuser" },
    });
    fireEvent.change(screen.getByPlaceholderText(/Password/i), {
      target: { value: "testpass" },
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Sign In/i }));
    });

    // 3. Should now be on Landing Page
    expect(screen.getByText(/Automate Your/i)).toBeInTheDocument();

    // 4. Navigate to Water Apps
    fireEvent.click(screen.getByText(/Water/i));
    expect(screen.getByText(/Water Systems/i)).toBeInTheDocument();
    expect(screen.getByText(/Choose an Application/i)).toBeInTheDocument();

    // 5. Navigate to Booster Set
    fireEvent.click(screen.getByText(/Booster Set/i));
    expect(
      screen.getAllByText(/Application Design Library/i)[0],
    ).toBeInTheDocument();

    // 6. Test Logout
    const logoutBtn = screen.getByText(/Log Out/i);
    await act(async () => {
      fireEvent.click(logoutBtn);
    });
    expect(screen.getByText(/Sign in to Designer Panel/i)).toBeInTheDocument();
  });
});
