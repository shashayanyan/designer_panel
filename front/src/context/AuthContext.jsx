import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(false); // Used only as a boolean flag now
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const verifyToken = async () => {
            try {
                // Check if we just logged in via Central Dashboard
                const params = new URLSearchParams(window.location.search);
                const dashboardToken = params.get('access_token');
                
                if (dashboardToken) {
                    localStorage.setItem('dashboard_token', dashboardToken);
                    // Clear the token from the URL for security
                    window.history.replaceState({}, document.title, window.location.pathname);
                }

                const tokenToUse = localStorage.getItem('dashboard_token');
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                
                const headers = {};
                if (tokenToUse) {
                    headers['Authorization'] = `Bearer ${tokenToUse}`;
                }

                const response = await fetch(`${apiUrl}/me`, {
                    credentials: 'include',
                    headers
                });
                if (response.ok) {
                    const userData = await response.json();
                    setUser(userData);
                    setToken(true);
                } else {
                    setToken(false);
                    setUser(null);
                }
            } catch (error) {
                console.error("Failed to verify authentication", error);
                setToken(false);
                setUser(null);
            } finally {
                setLoading(false);
            }
        };
        verifyToken();
    }, []);

    const login = (newToken, userData) => {
        // newToken is strictly ignored, relying on backend cookie
        setToken(true);
        setUser(userData);
    };

    const logout = async () => {
        setToken(false);
        setUser(null);
        localStorage.removeItem('dashboard_token');
        try {
            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const headers = {};
            // Optional: send token to backend if it needs to register a logout event
            const tokenToUse = localStorage.getItem('dashboard_token');
            if (tokenToUse) headers['Authorization'] = `Bearer ${tokenToUse}`;
            
            await fetch(`${apiUrl}/logout`, { method: 'POST', credentials: 'include', headers });
        } catch (error) {
            console.error("Logout failed", error);
        }
    };

    return (
        <AuthContext.Provider value={{ user, token, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};
