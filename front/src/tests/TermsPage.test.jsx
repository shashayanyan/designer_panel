import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { MemoryRouter } from "react-router-dom";
import TermsPage from "../pages/TermsPage";

const mockedUsedNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockedUsedNavigate,
  };
});

describe("TermsPage Component", () => {
  it("renders terms of use correctly", () => {
    render(
      <MemoryRouter>
        <TermsPage />
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: /Terms of Use/i, level: 1 }),
    ).toBeInTheDocument();
    expect(screen.getByText(/1. Acceptance of Terms/i)).toBeInTheDocument();
  });

  it("navigates home when back button is clicked", () => {
    render(
      <MemoryRouter>
        <TermsPage />
      </MemoryRouter>,
    );

    const backButton = screen.getByRole("button", { name: /← Go to Home/i });
    fireEvent.click(backButton);
    expect(mockedUsedNavigate).toHaveBeenCalledWith("/");
  });
});
