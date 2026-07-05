import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, vi } from "vitest";
import WaterPage from "../pages/WaterPage";
import React from "react";

const mockedNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useNavigate: () => mockedNavigate,
  };
});

describe("WaterPage", () => {
  it("renders the application grid correctly", () => {
    render(
      <BrowserRouter>
        <WaterPage />
      </BrowserRouter>,
    );
    expect(screen.getByText(/Choose an Application/i)).toBeInTheDocument();
    expect(screen.getByText(/Booster Set/i)).toBeInTheDocument();
    expect(screen.getByText(/Single Pump/i)).toBeInTheDocument();
  });

  it("navigates to booster set page when clicking the Booster Set card", () => {
    render(
      <BrowserRouter>
        <WaterPage />
      </BrowserRouter>,
    );
    const boosterCard = screen.getByText(/Booster Set/i).closest("button");
    fireEvent.click(boosterCard);
    expect(mockedNavigate).toHaveBeenCalledWith("/water/booster-set");
  });

  it("navigates back to home when back button is clicked", () => {
    render(
      <BrowserRouter>
        <WaterPage />
      </BrowserRouter>,
    );
    const backButton = screen.getByRole("button", { name: /← Back to Home/i });
    fireEvent.click(backButton);
    expect(mockedNavigate).toHaveBeenCalledWith("/");
  });
});
