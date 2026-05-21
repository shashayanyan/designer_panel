import { render, screen } from "@testing-library/react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import ProtectedRoute from "../components/ProtectedRoute";
import { AuthContext } from "../context/AuthContext";
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

  it("renders children when token is present", () => {
    render(
      <AuthContext.Provider value={{ token: "mock-token", loading: false }}>
        <MemoryRouter>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </MemoryRouter>
      </AuthContext.Provider>,
    );
    expect(screen.getByText("Protected Content")).toBeInTheDocument();
  });
});
