import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import FeedbackBubble from "../components/FeedbackBubble";
import { AuthContext } from "../context/AuthContext";

global.fetch = vi.fn();

describe("FeedbackBubble Component", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not render when user is not authenticated", () => {
    const { container } = render(
      <AuthContext.Provider value={{ token: false }}>
        <FeedbackBubble />
      </AuthContext.Provider>,
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders when authenticated, and opens form on click", async () => {
    render(
      <AuthContext.Provider value={{ token: true }}>
        <FeedbackBubble />
      </AuthContext.Provider>,
    );

    // Toggle bubble button should be present
    const toggleBtn = screen.getByRole("button", {
      name: /toggle feedback form/i,
    });
    expect(toggleBtn).toBeInTheDocument();

    // The popup should not be visible yet
    expect(screen.queryByText("Feedback")).not.toBeInTheDocument();

    // Click to open the popup
    await act(async () => {
      fireEvent.click(toggleBtn);
    });

    // Header and fields should now be visible
    expect(screen.getByText("Feedback")).toBeInTheDocument();
    expect(screen.getByLabelText(/category/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/comment/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /submit feedback/i }),
    ).toBeInTheDocument();
  });

  it("validates form input and submits feedback successfully", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ id: 1 }),
    });

    render(
      <AuthContext.Provider value={{ token: true }}>
        <FeedbackBubble />
      </AuthContext.Provider>,
    );

    const toggleBtn = screen.getByRole("button", {
      name: /toggle feedback form/i,
    });
    await act(async () => {
      fireEvent.click(toggleBtn);
    });

    const submitBtn = screen.getByRole("button", { name: /submit feedback/i });

    // Submit with empty comment should show error
    await act(async () => {
      fireEvent.click(submitBtn);
    });
    expect(
      screen.getByText(/please provide your feedback comment/i),
    ).toBeInTheDocument();

    // Fill comment and category
    const commentArea = screen.getByLabelText(/comment/i);
    const categorySelect = screen.getByLabelText(/category/i);

    fireEvent.change(commentArea, { target: { value: "A wonderful app!" } });
    fireEvent.change(categorySelect, { target: { value: "Feature Request" } });

    // Submit form
    await act(async () => {
      fireEvent.click(submitBtn);
    });

    // Check fetch parameters
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/feedback"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          category: "Feature Request",
          comment: "A wonderful app!",
          page_url: "/",
        }),
      }),
    );

    // Success message should appear
    expect(
      screen.getByText(
        /thank you! your feedback has been submitted successfully/i,
      ),
    ).toBeInTheDocument();
  });
});
