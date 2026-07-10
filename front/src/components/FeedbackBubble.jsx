import React, { useState, useContext } from "react";
import { X } from "lucide-react";
import { AuthContext } from "../context/AuthContext";
import "./FeedbackBubble.css";

function FeedbackBubble() {
  const { token } = useContext(AuthContext);
  const [isOpen, setIsOpen] = useState(false);
  const [category, setCategory] = useState("General");
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  // Only render if user is authenticated (token is true)
  if (!token) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!comment.trim()) {
      setError("Please provide your feedback comment.");
      return;
    }

    setIsSubmitting(true);
    setError("");

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const tokenToUse = localStorage.getItem("dashboard_token");
      const headers = {
        "Content-Type": "application/json",
      };
      if (tokenToUse) {
        headers["Authorization"] = `Bearer ${tokenToUse}`;
      }

      const response = await fetch(`${apiUrl}/api/v1/feedback`, {
        method: "POST",
        credentials: "include",
        headers,
        body: JSON.stringify({
          category,
          comment,
          page_url: window.location.pathname,
        }),
      });

      if (response.ok) {
        setSuccess(true);
        setComment("");
        setCategory("General");
        setTimeout(() => {
          setSuccess(false);
          setIsOpen(false);
        }, 2500);
      } else {
        const errorData = await response.json().catch(() => ({}));
        setError(
          errorData.detail || "Failed to submit feedback. Please try again.",
        );
      }
    } catch (err) {
      console.error("Feedback submission error", err);
      setError("Failed to submit feedback. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="feedback-container">
      {/* Floating Bubble Button */}
      <button
        className={`feedback-bubble-btn ${isOpen ? "active" : ""}`}
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle feedback form"
      >
        {isOpen ? "Close" : "Submit Feedback"}
      </button>

      {/* Feedback Form Modal/Popup */}
      {isOpen && (
        <div className="feedback-popup">
          <div className="feedback-popup-header">
            <h3>Feedback</h3>
            <button
              className="feedback-close-btn"
              onClick={() => setIsOpen(false)}
            >
              <X size={18} />
            </button>
          </div>

          {success ? (
            <div className="feedback-success-msg">
              <p>Thank you! Your feedback has been submitted successfully.</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="feedback-form">
              {error && <div className="feedback-error-msg">{error}</div>}

              <div className="feedback-field">
                <label htmlFor="feedback-category">Category</label>
                <select
                  id="feedback-category"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  <option value="General">General</option>
                  <option value="Bug">Bug Report</option>
                  <option value="Feature Request">Feature Request</option>
                </select>
              </div>

              <div className="feedback-field">
                <label htmlFor="feedback-comment">Comment</label>
                <textarea
                  id="feedback-comment"
                  value={comment}
                  onChange={(e) => setComment(e.target.value)}
                  placeholder="Share your thoughts or describe the issue..."
                  rows={4}
                  maxLength={1000}
                />
              </div>

              <button
                type="submit"
                className="feedback-submit-btn"
                disabled={isSubmitting}
              >
                {isSubmitting ? "Submitting..." : "Submit Feedback"}
              </button>
            </form>
          )}
        </div>
      )}
    </div>
  );
}

export default FeedbackBubble;
