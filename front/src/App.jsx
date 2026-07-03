import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import WaterPage from "./pages/WaterPage";
import BoosterSetPage from "./pages/BoosterSetPage";
import LoginPage from "./pages/LoginPage";
import TermsPage from "./pages/TermsPage";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import React, { useContext } from "react";
import ProtectedRoute from "./components/ProtectedRoute";
import FeedbackBubble from "./components/FeedbackBubble";

function TopNav() {
  const { token, logout } = useContext(AuthContext);
  if (!token) return null;

  return (
    <div className="logout-nav fade-in">
      <button onClick={logout} className="btn-secondary">
        Log Out
      </button>
    </div>
  );
}

function Footer() {
  return (
    <footer className="global-footer fade-in">
      <p>
        © 2026 Motor Control Asset Library. All rights reserved.
        <a href="/terms" target="_blank" rel="noopener noreferrer">
          Terms of Use
        </a>
      </p>
    </footer>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <TopNav />
        <FeedbackBubble />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/terms" element={<TermsPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <LandingPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/water"
            element={
              <ProtectedRoute>
                <WaterPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/water/booster-set"
            element={
              <ProtectedRoute>
                <BoosterSetPage />
              </ProtectedRoute>
            }
          />
        </Routes>
        <Footer />
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
