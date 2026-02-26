import { useNavigate } from 'react-router-dom'
import './WaterPage.css'

const applications = [
    {
        id: 'single-pump',
        label: 'Single Pump',
        icon: '⚙️',
        description: 'Single motor pump control',
        available: false,
    },
    {
        id: 'mcc-feeders',
        label: 'MCC Stand. Feeders',
        icon: '🔌',
        description: 'Motor control centre feeders',
        available: false,
    },
    {
        id: 'booster-set',
        label: 'Booster Set',
        icon: '🚀',
        description: 'Multi-pump booster systems',
        available: true,
    },
    {
        id: 'tank-level',
        label: 'Tank Level Control',
        icon: '📊',
        description: 'Tank level monitoring & control',
        available: false,
    },
]

function WaterPage() {
    const navigate = useNavigate()

    return (
        <div className="water">
            <div className="water__ambient" />

            <header className="water__header fade-in">
                <button className="btn-secondary" onClick={() => navigate('/')}>
                    ← Back to Home
                </button>
            </header>

            <div className="water__content">
                <div className="water__intro fade-in">
                    <div className="water__badge">Water Systems</div>
                    <h1 className="water__title">Choose an Application</h1>
                    <p className="water__description">
                        Select the type of water system application you want to configure.
                    </p>
                </div>

                <div className="water__grid">
                    {applications.map((app, i) => (
                        <button
                            key={app.id}
                            id={`app-${app.id}`}
                            className={`water__app-card glass-card fade-in fade-in-delay-${i + 1} ${!app.available ? 'water__app-card--disabled' : ''
                                }`}
                            onClick={() => app.available && navigate('/water/booster-set')}
                            disabled={!app.available}
                        >
                            <div className="water__app-icon">{app.icon}</div>
                            <div className="water__app-info">
                                <span className="water__app-label">{app.label}</span>
                                <span className="water__app-desc">{app.description}</span>
                            </div>
                            {app.available ? (
                                <span className="water__app-arrow">→</span>
                            ) : (
                                <span className="water__app-badge-soon">Soon</span>
                            )}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default WaterPage
