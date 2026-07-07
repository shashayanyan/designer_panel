import React, { useContext, useEffect, useState } from "react";
import PropTypes from "prop-types";
import { Navigate, useLocation } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";
import { supabase } from "../supabase";


function ProtectedRoute({ children }) {
  const { token, loading: authLoading } = useContext(AuthContext);
  const location = useLocation();
  const [checkingAccess, setCheckingAccess] = useState(true);
  const [hasAccess, setHasAccess] = useState(false);

  useEffect(() => {
    let active = true;
    if (authLoading) return;
    if (!token) {
      setCheckingAccess(false);
      return;
    }

    const checkPermission = async () => {
      try {
        const isPlaceholder = import.meta.env.VITE_SUPABASE_URL === undefined || import.meta.env.VITE_SUPABASE_URL.includes("placeholder");
        if (isPlaceholder) {
          if (active) {
            setHasAccess(true);
            setCheckingAccess(false);
          }
          return;
        }

        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        if (sessionError || !session || !session.user) {
          if (active) {
            setHasAccess(false);
            setCheckingAccess(false);
          }
          return;
        }

        const userId = session.user.id;
        const { data, error } = await supabase
          .from("user_permissions")
          .select("allowed_apps")
          .eq("user_id", userId)
          .single();

        if (error) {
          console.error("Error fetching user permissions", error);
          if (active) {
            setHasAccess(false);
            setCheckingAccess(false);
          }
          return;
        }

        const isAllowed = data?.allowed_apps?.includes("designer");
        if (active) {
          setHasAccess(!!isAllowed);
          setCheckingAccess(false);
        }
      } catch (err) {
        console.error("Access check failed", err);
        if (active) {
          setHasAccess(false);
          setCheckingAccess(false);
        }
      }
    };

    checkPermission();

    return () => {
      active = false;
    };
  }, [token, authLoading]);

  // Keep test alignment: "renders loading state when auth is loading" -> "Loading..."
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (checkingAccess) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-[#f8fafc]">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#009305] mb-4"></div>
        <p className="text-[#47694e] font-medium">Checking authorization...</p>
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!hasAccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-blue-50 p-4">
        <div className="glass-card max-w-md w-full p-8 text-center shadow-2xl border border-white/20 backdrop-blur-xl bg-white/70 relative overflow-hidden fade-in">
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-red-500 to-orange-500" />
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6 text-red-600 animate-pulse">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m0-10.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.75c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.57-.598-3.75h-.152c-3.196 0-6.1-1.249-8.25-3.286zm0 13.036h.008v.008H12v-.008z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-[#1e3b22] mb-4">Access Denied</h2>
          <p className="text-[#47694e] text-sm leading-relaxed mb-8">
            You do not have permission to access the Application Design Library. Please contact your system administrator.
          </p>
          <button
            onClick={() => {
              window.location.href = "/";
            }}
            className="btn-primary w-full py-3 bg-[#009305] hover:bg-[#2563eb] text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return children;
}

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default ProtectedRoute;

