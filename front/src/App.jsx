import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import WaterPage from './pages/WaterPage'
import BoosterSetPage from './pages/BoosterSetPage'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<LandingPage />} />
                <Route path="/water" element={<WaterPage />} />
                <Route path="/water/booster-set" element={<BoosterSetPage />} />
            </Routes>
        </BrowserRouter>
    )
}

export default App
