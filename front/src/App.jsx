import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import WaterPage from './pages/WaterPage'
import BoosterSetPage from './pages/BoosterSetPage'
import LoginPage from './pages/LoginPage'
import { AuthProvider, AuthContext } from './context/AuthContext'
import { useContext } from 'react'
import ProtectedRoute from './components/ProtectedRoute'

function TopNav() {
    const { token, logout } = useContext(AuthContext);
    if (!token) return null;

    return (
        <div className="logout-nav fade-in">
            <button
                onClick={logout}
                className="btn-secondary"
            >
                Log Out
            </button>
        </div>
    );
}

function App() {
    return (
        <AuthProvider>
            <BrowserRouter>
                <TopNav />
                <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/" element={<ProtectedRoute><LandingPage /></ProtectedRoute>} />
                    <Route path="/water" element={<ProtectedRoute><WaterPage /></ProtectedRoute>} />
                    <Route path="/water/booster-set" element={<ProtectedRoute><BoosterSetPage /></ProtectedRoute>} />
                </Routes>
            </BrowserRouter>
        </AuthProvider>
    )
}

export default App
