import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import './BoosterSetPage.css'

const CONFIG_OPTIONS = {
    incomers: { label: 'Number of Incomers', options: ['1', '2'] },
    pumps: { label: 'Number of Pumps', options: ['2', '3', '4'] },
    motorPower: {
        label: 'Motor Power Rate (kW)',
        options: ['4', '7.5', '11', '15', '22.5', '30', '37', '45'],
    },
    motorStart: {
        label: 'Type of Motor Start',
        options: ['DOL', 'Star-Delta', 'Soft Starter', 'Variable Speed Drive'],
    },
    ipRating: { label: 'IP Rating', options: ['IP23', 'IP54'] },
    communication: {
        label: 'Communication',
        options: ['No', 'ModbusTCP', 'ProfiNet'],
    },
}

const ASSET_LIST = [
    'Data Sheet',
    'Single Line Diagram',
    'Bill of Materials',
    'Drawings',
    'Specification',
    'BIM Object',
]

function BoosterSetPage() {
    const navigate = useNavigate()

    const [config, setConfig] = useState({
        incomers: '',
        pumps: '',
        motorPower: '',
        motorStart: '',
        ipRating: '',
        communication: '',
    })

    const [selectedAssets, setSelectedAssets] = useState(
        ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: false }), {})
    )

    const allFieldsFilled = useMemo(
        () => Object.values(config).every((v) => v !== ''),
        [config]
    )

    const handleConfigChange = (key, value) => {
        setConfig((prev) => ({ ...prev, [key]: value }))
    }

    const toggleAsset = (asset) => {
        setSelectedAssets((prev) => ({ ...prev, [asset]: !prev[asset] }))
    }

    const handleDownload = () => {
        alert(
            'Download triggered!\n\nSelected assets:\n' +
            Object.entries(selectedAssets)
                .filter(([, v]) => v)
                .map(([k]) => `• ${k}`)
                .join('\n')
        )
    }

    const pumpCount = parseInt(config.pumps) || 0
    const incomerCount = parseInt(config.incomers) || 0


    return (
        <div className="booster">
            {/* ─── Section 1: Header ─── */}
            <header className="booster__header fade-in">
                <div className="booster__header-left">
                    <h1 className="booster__title">Motor Control Asset Library</h1>
                    <p className="booster__subtitle">
                        Configure your booster set parameters and download the asset
                        package.
                    </p>
                </div>
                <div className="booster__header-right">
                    <button
                        className="btn-secondary"
                        id="btn-back-apps"
                        onClick={() => navigate('/water')}
                    >
                        ← Back to Water Apps
                    </button>
                    <button
                        className="btn-secondary"
                        id="btn-back-home"
                        onClick={() => navigate('/')}
                    >
                        ← Back to Home
                    </button>
                </div>
            </header>

            {/* ─── Main Body ─── */}
            <div className="booster__body">
                {/* ─── Left Column ─── */}
                <aside className="booster__sidebar">
                    {/* Section 2: Configuration */}
                    <section className="booster__config glass-card fade-in fade-in-delay-1">
                        <h2 className="booster__section-title">Configuration</h2>
                        <div className="booster__fields">
                            {Object.entries(CONFIG_OPTIONS).map(([key, { label, options }]) => (
                                <div className="booster__field" key={key}>
                                    <label className="booster__label" htmlFor={`config-${key}`}>
                                        {label}
                                    </label>
                                    <select
                                        id={`config-${key}`}
                                        className="booster__select"
                                        value={config[key]}
                                        onChange={(e) => handleConfigChange(key, e.target.value)}
                                    >
                                        <option value="" disabled>
                                            Select…
                                        </option>
                                        {options.map((opt) => (
                                            <option key={opt} value={opt}>
                                                {opt}
                                                {key === 'motorPower' ? ' kW' : ''}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            ))}
                        </div>
                    </section>

                    {/* Section 4: Assets */}
                    <section className="booster__assets glass-card fade-in fade-in-delay-3">
                        <h2 className="booster__section-title">Assets</h2>
                        <div className="booster__checklist">
                            {ASSET_LIST.map((asset) => (
                                <label className="booster__check-item" key={asset}>
                                    <input
                                        type="checkbox"
                                        checked={selectedAssets[asset]}
                                        onChange={() => toggleAsset(asset)}
                                        className="booster__checkbox"
                                    />
                                    <span className="booster__check-label">{asset}</span>
                                </label>
                            ))}
                        </div>
                        <button
                            className="btn-primary booster__download-btn"
                            id="btn-download"
                            disabled={!allFieldsFilled}
                            onClick={handleDownload}
                        >
                            <span>📦</span> Download Package
                        </button>
                    </section>
                </aside>

                {/* ─── Section 3: Single Line Diagram ─── */}
                <section className="booster__diagram glass-card fade-in fade-in-delay-2">
                    <h2 className="booster__section-title">Single Line Diagram</h2>

                    {/* Selection bubbles bar */}
                    <div className="booster__bubbles-bar">
                        {Object.entries(CONFIG_OPTIONS).map(([key, { label }]) => {
                            const value = config[key]
                            const hasFilled = value !== ''

                            let displayValue = value
                            if (key === 'motorPower' && value) displayValue = `${value} kW`
                            if (key === 'incomers' && value) displayValue = `${value} Incomer${value !== '1' ? 's' : ''}`
                            if (key === 'pumps' && value) displayValue = `${value} Pumps`

                            return (
                                <div
                                    key={key}
                                    className={`booster__bubble ${hasFilled ? 'booster__bubble--filled' : ''}`}
                                >
                                    <span className="booster__bubble-value">
                                        {hasFilled ? displayValue : label}
                                    </span>
                                </div>
                            )
                        })}
                    </div>

                    {/* Diagram area */}
                    <div className="booster__diagram-canvas">
                        {!allFieldsFilled ? (
                            <div className="booster__diagram-placeholder">
                                <div className="booster__diagram-placeholder-icon">⚡</div>
                                <p>Complete the configuration to see the diagram</p>
                            </div>
                        ) : (
                            <svg
                                viewBox="0 0 800 520"
                                className="booster__svg"
                                xmlns="http://www.w3.org/2000/svg"
                            >
                                {/* Main bus bar */}
                                <line x1="100" y1="60" x2="700" y2="60" stroke="#3b82f6" strokeWidth="3" />
                                <text x="400" y="40" textAnchor="middle" fill="#475569" fontSize="13" fontFamily="Inter">Main Bus</text>

                                {/* Incomers */}
                                {Array.from({ length: incomerCount }).map((_, i) => {
                                    const x = 100 + i * 80
                                    return (
                                        <g key={`incomer-${i}`}>
                                            <line x1={x} y1="10" x2={x} y2="60" stroke="#06b6d4" strokeWidth="2" />
                                            <rect x={x - 14} y="2" width="28" height="14" rx="3" fill="#e0f2fe" stroke="#06b6d4" strokeWidth="1" />
                                            <text x={x} y="12" textAnchor="middle" fill="#0e7490" fontSize="8" fontFamily="Inter">IN{i + 1}</text>
                                        </g>
                                    )
                                })}

                                {/* Pump feeders */}
                                {Array.from({ length: pumpCount }).map((_, i) => {
                                    const spacing = 600 / (pumpCount + 1)
                                    const x = 100 + spacing * (i + 1)
                                    const motorLabel = config.motorStart === 'Variable Speed Drive' ? 'VSD' :
                                        config.motorStart === 'Soft Starter' ? 'SS' :
                                            config.motorStart === 'Star-Delta' ? 'S-D' : 'DOL'
                                    return (
                                        <g key={`pump-${i}`}>
                                            <line x1={x} y1="60" x2={x} y2="120" stroke="#3b82f6" strokeWidth="2" />
                                            <rect x={x - 16} y="120" width="32" height="20" rx="4" fill="rgba(59,130,246,0.1)" stroke="#3b82f6" strokeWidth="1" />
                                            <text x={x} y="134" textAnchor="middle" fill="#2563eb" fontSize="8" fontFamily="Inter">CB</text>
                                            <line x1={x} y1="140" x2={x} y2="170" stroke="#3b82f6" strokeWidth="2" />
                                            <rect x={x - 22} y="170" width="44" height="28" rx="4" fill="rgba(139,92,246,0.1)" stroke="#8b5cf6" strokeWidth="1" />
                                            <text x={x} y="188" textAnchor="middle" fill="#7c3aed" fontSize="9" fontWeight="600" fontFamily="Inter">{motorLabel}</text>
                                            <line x1={x} y1="198" x2={x} y2="240" stroke="#3b82f6" strokeWidth="2" />
                                            <circle cx={x} cy="268" r="28" fill="rgba(22,163,74,0.08)" stroke="#16a34a" strokeWidth="1.5" />
                                            <text x={x} y="264" textAnchor="middle" fill="#16a34a" fontSize="10" fontFamily="Inter">M</text>
                                            <text x={x} y="278" textAnchor="middle" fill="#15803d" fontSize="8" fontFamily="Inter">{config.motorPower}kW</text>
                                            <text x={x} y="315" textAnchor="middle" fill="#475569" fontSize="10" fontFamily="Inter">Pump {i + 1}</text>
                                        </g>
                                    )
                                })}

                                {/* Footer info */}
                                <text x="100" y="370" fill="#475569" fontSize="11" fontFamily="Inter">IP Rating: {config.ipRating}</text>
                                <text x="100" y="390" fill="#475569" fontSize="11" fontFamily="Inter">Communication: {config.communication === 'No' ? 'None' : config.communication}</text>

                                {/* Communication bus */}
                                {config.communication !== 'No' && (
                                    <g>
                                        <line x1="100" y1="420" x2="700" y2="420" stroke="#d97706" strokeWidth="2" strokeDasharray="8 4" />
                                        <text x="400" y="445" textAnchor="middle" fill="#d97706" fontSize="11" fontFamily="Inter">{config.communication} Bus</text>
                                        {Array.from({ length: pumpCount }).map((_, i) => {
                                            const spacing = 600 / (pumpCount + 1)
                                            const x = 100 + spacing * (i + 1)
                                            return (
                                                <line key={`comm-${i}`} x1={x} y1="296" x2={x} y2="420" stroke="#d97706" strokeWidth="1" strokeDasharray="4 3" />
                                            )
                                        })}
                                    </g>
                                )}
                            </svg>
                        )}
                    </div>
                </section>
            </div>
        </div>
    )
}

export default BoosterSetPage
