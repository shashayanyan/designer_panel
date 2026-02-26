import { useNavigate } from 'react-router-dom'
import './LandingPage.css'

function LandingPage() {
    const navigate = useNavigate()

    return (
        <div className="landing">
            {/* Ambient background glow */}
            <div className="landing__ambient" />

            <div className="landing__content fade-in">
                <div className="landing__badge">Designer Panel</div>
                <h1 className="landing__title">
                    Automate Your <span className="landing__highlight">Specification Projects</span>
                </h1>
                <p className="landing__description">
                    Configure your project setup, select assets, and download everything
                    you need — all in one place. Choose a discipline to get started.
                </p>
            </div>

            <div className="landing__choices">
                <button
                    className="landing__card fade-in fade-in-delay-1"
                    id="card-water"
                    onClick={() => navigate('/water')}
                >
                    <img
                        src="/images/water-bg.png"
                        alt="Water systems"
                        className="landing__card-bg"
                    />
                    <div className="landing__card-overlay" />
                    <div className="landing__card-content">
                        <div className="landing__card-icon">💧</div>
                        <span className="landing__card-label">Water</span>
                        <span className="landing__card-sub">Pumps, boosters & controls</span>
                    </div>
                </button>

                <button
                    className="landing__card landing__card--disabled fade-in fade-in-delay-2"
                    id="card-buildings"
                    disabled
                >
                    <img
                        src="/images/buildings-bg.png"
                        alt="Building systems"
                        className="landing__card-bg"
                    />
                    <div className="landing__card-overlay" />
                    <div className="landing__card-content">
                        <div className="landing__card-icon">🏗️</div>
                        <span className="landing__card-label">Buildings</span>
                        <span className="landing__card-sub">Coming soon</span>
                    </div>
                </button>
            </div>
        </div>
    )
}

export default LandingPage
