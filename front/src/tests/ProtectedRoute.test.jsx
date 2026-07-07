import { render, screen, act, waitFor } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import ProtectedRoute from "../components/ProtectedRoute";
import { AuthContext } from "../context/AuthContext";
import { supabase } from "../supabase";
import React from "react";

describe("ProtectedRoute", () => {
  it("renders loading state when auth is loading", () => {
    render(
      <AuthContext.Provider value={{ token: null, loading: true }}>
        <MemoryRouter>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("redirects to login when no token is present", () => {
    render(
      <AuthContext.Provider value={{ token: null, loading: false }}>
        <MemoryRouter initialEntries={["/protected"]}>
          <Routes>
            <Route path="/login" element={<div>Login Page</div>} />
            <Route
              path="/protected"
              element={
                <ProtectedRoute>
                  <div>Protected Content</div>
                </ProtectedRoute>
              }
            />
          </Routes>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    expect(screen.getByText("Login Page")).toBeInTheDocument();
    expect(screen.queryByText("Protected Content")).not.toBeInTheDocument();
  });

  it("renders children when token is present and user has designer permission", async () => {
    vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
      data: { session: { user: { id: "allowed-user-id" } } },
      error: null,
    });

    const mockSingle = vi.fn().mockResolvedValueOnce({
      data: { allowed_apps: ["designer"] },
      error: null,
    });
    vi.mocked(supabase.from).mockReturnValueOnce({
      select: () => ({
        eq: () => ({
          single: mockSingle,
        }),
      }),
    });

    await act(async () => {
      render(
        <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
          <MemoryRouter>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>,
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Protected Content")).toBeInTheDocument();
    });
  });

  it("renders Access Denied screen when allowed_apps does not contain designer", async () => {
    vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
      data: { session: { user: { id: "unauthorized-user-id" } } },
      error: null,
    });

    const mockSingle = vi.fn().mockResolvedValueOnce({
      data: { allowed_apps: ["other-app"] },
      error: null,
    });
    vi.mocked(supabase.from).mockReturnValueOnce({
      select: () => ({
        eq: () => ({
          single: mockSingle,
        }),
      }),
    });

    await act(async () => {
      render(
        <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
          <MemoryRouter>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>,
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Access Denied")).toBeInTheDocument();
      expect(screen.getByText(/You do not have permission/i)).toBeInTheDocument();
    });
  });

  it("renders Access Denied on database query error", async () => {
    vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
      data: { session: { user: { id: "error-user-id" } } },
      error: null,
    });

    const mockSingle = vi.fn().mockResolvedValueOnce({
      data: null,
      error: { message: "Database failure" },
    });
    vi.mocked(supabase.from).mockReturnValueOnce({
      select: () => ({
        eq: () => ({
          single: mockSingle,
        }),
      }),
    });

    await act(async () => {
      render(
        <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
          <MemoryRouter>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>,
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Access Denied")).toBeInTheDocument();
    });
  });

  it("renders Access Denied on getSession error and handles redirect button click", async () => {
    vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
      data: { session: null },
      error: { message: "Auth error" },
    });

    const originalLocation = window.location;
    delete window.location;
    window.location = { href: "" };

    await act(async () => {
      render(
        <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
          <MemoryRouter>
            <ProtectedRoute>
              <div>Protected Content</div>
            </ProtectedRoute>
          </MemoryRouter>
        </AuthContext.Provider>,
      );
    });

    await waitFor(() => {
      expect(screen.getByText("Access Denied")).toBeInTheDocument();
    });

    const btn = screen.getByRole("button", { name: /Back to Dashboard/i });
    btn.click();
    expect(window.location.href).toBe("/");

    window.location = originalLocation;
  });
});

