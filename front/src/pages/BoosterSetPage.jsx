import { useState, useMemo, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import JSZip from 'jszip'
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

const CircuitBreaker = ({ x, y, label }) => (
    <g transform={`translate(${x}, ${y})`}>
        <text x="25" y="15" fontSize="10" fill="#475569" fontFamily="monospace">{label}</text>
        {/* Switch Contacts */}
        <line x1="-10" y1="0" x2="-5" y2="20" stroke="currentColor" strokeWidth="1.5" />
        <line x1="0" y1="0" x2="5" y2="20" stroke="currentColor" strokeWidth="1.5" />
        <line x1="10" y1="0" x2="15" y2="20" stroke="currentColor" strokeWidth="1.5" />
        {/* Ganging Bar */}
        <line x1="-8" y1="10" x2="12" y2="10" stroke="currentColor" strokeWidth="2" strokeDasharray="2 2" />
        {/* Lines continuing */}
        <line x1="-10" y1="20" x2="-10" y2="30" stroke="currentColor" strokeWidth="1.5" />
        <line x1="0" y1="20" x2="0" y2="30" stroke="currentColor" strokeWidth="1.5" />
        <line x1="10" y1="20" x2="10" y2="30" stroke="currentColor" strokeWidth="1.5" />
    </g>
)

const MotorSymbol = ({ x, y, label, power }) => (
    <g transform={`translate(${x}, ${y})`}>
        <circle cx="0" cy="20" r="16" fill="white" stroke="currentColor" strokeWidth="2" />
        <text x="0" y="24" textAnchor="middle" fontSize="12" fontFamily="sans-serif" fill="currentColor">M</text>
        <circle cx="-10" cy="0" r="2" fill="currentColor" />
        <circle cx="0" cy="0" r="2" fill="currentColor" />
        <circle cx="10" cy="0" r="2" fill="currentColor" />
        <text x="0" y="50" textAnchor="middle" fontSize="10" fill="#475569" fontFamily="monospace">{label}</text>
        <text x="0" y="65" textAnchor="middle" fontSize="10" fill="#475569" fontFamily="monospace">{power} kW</text>
    </g>
)

const StarterBlock = ({ x, y, type }) => {
    let symbol = null;
    if (type === 'Variable Speed Drive') {
        symbol = (
            <g>
                <circle cx="0" cy="20" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="14" x2="-4" y2="26" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="20" x2="4" y2="15" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="20" x2="4" y2="25" stroke="currentColor" strokeWidth="1" />
                <polygon points="1,24 5,26 4,22" fill="currentColor" />
            </g>
        )
    } else if (type === 'Soft Starter') {
        symbol = (
            <g>
                <line x1="-8" y1="20" x2="8" y2="20" stroke="currentColor" strokeWidth="1" />
                <polygon points="-4,15 4,20 -4,25" fill="none" stroke="currentColor" strokeWidth="1" />
                <line x1="4" y1="15" x2="4" y2="25" stroke="currentColor" strokeWidth="1" />
                <line x1="4" y1="25" x2="8" y2="28" stroke="currentColor" strokeWidth="1" />
            </g>
        )
    } else if (type === 'Star-Delta') {
        symbol = <text x="0" y="24" textAnchor="middle" fontSize="12" fill="currentColor">Y/Δ</text>
    } else {
        // DOL (Contactor + Thermal Overload simplified)
        symbol = (
            <g>
                <rect x="-11" y="16" width="6" height="8" fill="currentColor" />
                <rect x="-3" y="16" width="6" height="8" fill="currentColor" />
                <rect x="5" y="16" width="6" height="8" fill="currentColor" />
            </g>
        )
    }

    return (
        <g transform={`translate(${x}, ${y})`}>
            <rect x="-18" y="0" width="36" height="40" fill="white" stroke="currentColor" strokeWidth="1.5" />
            {symbol}
        </g>
    )
}

function BoosterSetPage() {
    const navigate = useNavigate()
    const svgRef = useRef(null)

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

    const handleDownload = async () => {
        const zip = new JSZip()

        const filesToFetch = [
            "ATV6A0C20Q4-SH-XX-CB-IP54.dwg",
            "ATV6A0C20Q4-SH-XX-CB-IP54.pdf",
            "ApplicationPack_WaterBooster_3x30kW_VSD_IP54_v1.xlsx",
            "Application_Spec_Appendix_WaterBooster_3x30kW_VSD_IP54_v1.docx",
            "SpecTextBlocks_WaterBooster_3x30kW_VSD_IP54_v1.txt"
        ]

        for (const fileName of filesToFetch) {
            try {
                const response = await fetch(`/documents/booster-set/${fileName}`)
                if (response.ok) {
                    const blob = await response.blob()
                    zip.file(fileName, blob)
                } else {
                    console.error(`Failed to fetch ${fileName}`)
                }
            } catch (e) {
                console.error(`Error fetching ${fileName}:`, e)
            }
        }

        if (svgRef.current) {
            const svgData = new XMLSerializer().serializeToString(svgRef.current)
            zip.file("SingleLineDiagram.svg", svgData)

            // Generate PNG
            await new Promise((resolve) => {
                const canvas = document.createElement("canvas")
                // Use the viewBox dimensions of the SVG
                canvas.width = 900
                canvas.height = 550
                const ctx = canvas.getContext("2d")

                const img = new Image()
                const svgBlob = new Blob([svgData], { type: "image/svg+xml;charset=utf-8" })
                const url = URL.createObjectURL(svgBlob)

                img.onload = () => {
                    ctx.fillStyle = "white"
                    ctx.fillRect(0, 0, canvas.width, canvas.height)
                    ctx.drawImage(img, 0, 0)
                    canvas.toBlob((blob) => {
                        if (blob) {
                            zip.file("SingleLineDiagram.png", blob)
                        }
                        URL.revokeObjectURL(url)
                        resolve()
                    }, "image/png")
                }

                img.onerror = () => {
                    console.error("Failed to render SVG to PNG")
                    URL.revokeObjectURL(url)
                    resolve() // Resolve anyway to proceed with ZIP generation
                }
                img.src = url
            })
        }

        try {
            const zipBlob = await zip.generateAsync({ type: "blob" })
            const url = URL.createObjectURL(zipBlob)
            const a = document.createElement('a')
            a.href = url
            a.download = "WaterBooster-3-Pumps-30kW-Asset-Pack.zip"
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
        } catch (e) {
            console.error("Error generating zip:", e)
            alert("Failed to generate zip file.")
        }
    }

    const pumpCount = parseInt(config.pumps) || 0
    const incomerCount = parseInt(config.incomers) || 0

    const busYStart = 120;
    const busSpacing = 10;
    const busLines = [busYStart, busYStart + busSpacing, busYStart + busSpacing * 2, busYStart + busSpacing * 4]; // L1, L2, L3, PE(spaced extra)

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
                        <button
                            className="btn-reset"
                            style={{ marginTop: 'var(--space-md)', width: '100%' }}
                            id="btn-reset-config"
                            onClick={() => setConfig({
                                incomers: '',
                                pumps: '',
                                motorPower: '',
                                motorStart: '',
                                ipRating: '',
                                communication: '',
                            })}
                        >
                            Reset
                        </button>
                    </section>

                    {/* Section 4: Assets */}
                    <section className="booster__assets glass-card fade-in fade-in-delay-3">
                        <h2 className="booster__section-title">Assets</h2>
                        <div className="booster__asset-buttons">
                            <button
                                className="btn-secondary"
                                id="btn-select-all"
                                onClick={() => {
                                    ASSET_LIST.forEach((asset) => {
                                        setSelectedAssets((prev) => ({ ...prev, [asset]: true }))
                                    })
                                }}
                            >
                                Select All
                            </button>
                            <button
                                className="btn-secondary"
                                id="btn-clear-selection"
                                onClick={() => {
                                    ASSET_LIST.forEach((asset) => {
                                        setSelectedAssets((prev) => ({ ...prev, [asset]: false }))
                                    })
                                }}
                            >
                                Clear All
                            </button>
                        </div>
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
                            <svg ref={svgRef} viewBox="0 0 900 550" className="booster__svg" xmlns="http://www.w3.org/2000/svg" style={{ minWidth: '800px', backgroundColor: 'white' }}>
                                <g stroke="#0f172a" fill="#0f172a">

                                    {/* --- 1. Main Busbars (4 Wires: L1, L2, L3, PE) --- */}
                                    <line x1="50" y1={busLines[0]} x2="850" y2={busLines[0]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[1]} x2="850" y2={busLines[1]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[2]} x2="850" y2={busLines[2]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[3]} x2="850" y2={busLines[3]} strokeWidth="2" strokeDasharray="8 4" stroke="#16a34a" />

                                    <text x="30" y={busLines[0] + 4} fontSize="10" fontFamily="monospace">L1</text>
                                    <text x="30" y={busLines[1] + 4} fontSize="10" fontFamily="monospace">L2</text>
                                    <text x="30" y={busLines[2] + 4} fontSize="10" fontFamily="monospace">L3</text>
                                    <text x="30" y={busLines[3] + 4} fontSize="10" fontFamily="monospace" fill="#16a34a">PE</text>

                                    {/* --- 2. Incomers --- */}
                                    {Array.from({ length: incomerCount }).map((_, i) => {
                                        const xPos = 120 + (i * 120);
                                        return (
                                            <g key={`incomer-${i}`}>
                                                {/* Incoming lines from top */}
                                                <line x1={xPos - 10} y1="40" x2={xPos - 10} y2="60" strokeWidth="1.5" />
                                                <line x1={xPos} y1="40" x2={xPos} y2="60" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="40" x2={xPos + 10} y2="60" strokeWidth="1.5" />

                                                <CircuitBreaker x={xPos} y={60} label={`QF${i + 1}`} />

                                                {/* Connecting to Busbars */}
                                                <line x1={xPos - 10} y1="90" x2={xPos - 10} y2={busLines[0]} strokeWidth="1.5" />
                                                <line x1={xPos} y1="90" x2={xPos} y2={busLines[1]} strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="90" x2={xPos + 10} y2={busLines[2]} strokeWidth="1.5" />

                                                <circle cx={xPos - 10} cy={busLines[0]} r="3" />
                                                <circle cx={xPos} cy={busLines[1]} r="3" />
                                                <circle cx={xPos + 10} cy={busLines[2]} r="3" />
                                            </g>
                                        )
                                    })}

                                    {/* ATS / ABP Interlock if 2 Incomers */}
                                    {incomerCount === 2 && (
                                        <g>
                                            <line x1="140" y1="70" x2="220" y2="70" strokeWidth="1.5" strokeDasharray="4 4" />
                                            <rect x="165" y="62" width="30" height="16" fill="white" stroke="#0f172a" strokeWidth="1.5" />
                                            <text x="180" y="74" textAnchor="middle" fontSize="10" fontFamily="sans-serif">ATS</text>
                                        </g>
                                    )}

                                    {/* --- 3. Pump Feeders --- */}
                                    {Array.from({ length: pumpCount }).map((_, i) => {
                                        const xPos = 400 + (i * 130);
                                        return (
                                            <g key={`pump-${i}`}>
                                                {/* Tap off from Busbars */}
                                                <circle cx={xPos - 10} cy={busLines[0]} r="3" />
                                                <circle cx={xPos} cy={busLines[1]} r="3" />
                                                <circle cx={xPos + 10} cy={busLines[2]} r="3" />

                                                <line x1={xPos - 10} y1={busLines[0]} x2={xPos - 10} y2="200" strokeWidth="1.5" />
                                                <line x1={xPos} y1={busLines[1]} x2={xPos} y2="200" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1={busLines[2]} x2={xPos + 10} y2="200" strokeWidth="1.5" />

                                                {/* Feeder Circuit Breaker */}
                                                <CircuitBreaker x={xPos} y={200} label={`QM${i + 1}`} />

                                                {/* Lines to Starter */}
                                                <line x1={xPos - 10} y1="230" x2={xPos - 10} y2="260" strokeWidth="1.5" />
                                                <line x1={xPos} y1="230" x2={xPos} y2="260" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="230" x2={xPos + 10} y2="260" strokeWidth="1.5" />

                                                {/* Motor Starter */}
                                                <StarterBlock x={xPos} y={260} type={config.motorStart} />

                                                {/* Lines to Motor */}
                                                <line x1={xPos - 10} y1="300" x2={xPos - 10} y2="340" strokeWidth="1.5" />
                                                <line x1={xPos} y1="300" x2={xPos} y2="340" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="300" x2={xPos + 10} y2="340" strokeWidth="1.5" />

                                                {/* Motor */}
                                                <MotorSymbol x={xPos} y={340} label={`Pump ${i + 1}`} power={config.motorPower} />

                                                {/* PE / Ground connection from Motor to Busbar 4 */}
                                                <line x1={xPos - 16} y1={360} x2={xPos - 30} y2={360} stroke="#16a34a" strokeWidth="1.5" />
                                                <line x1={xPos - 30} y1={360} x2={xPos - 30} y2={busLines[3]} stroke="#16a34a" strokeWidth="1.5" strokeDasharray="4 2" />
                                                <circle cx={xPos - 30} cy={busLines[3]} r="3" fill="#16a34a" />
                                            </g>
                                        )
                                    })}
                                    {/* --- 4. Communication Bus (Dashed Data Network) --- */}
                                    {config.communication !== 'No' && (
                                        <g>
                                            {/* Main Comm Bus Line */}
                                            <line x1="50" y1="460" x2="850" y2="460" stroke="#8b5cf6" strokeWidth="1.5" strokeDasharray="6 4" />
                                            <text x="60" y="455" fontSize="10" fill="#8b5cf6" fontFamily="monospace" fontWeight="bold">
                                                {config.communication} Network
                                            </text>

                                            {/* Connections from Comm Bus to each Starter */}
                                            {Array.from({ length: pumpCount }).map((_, i) => {
                                                const xPos = 400 + (i * 130);
                                                // The starter block is 36px wide (-18 to +18). We connect to the right side of it.
                                                return (
                                                    <g key={`comm-link-${i}`}>
                                                        <line x1={xPos + 18} y1="280" x2={xPos + 18} y2="460" stroke="#8b5cf6" strokeWidth="1" strokeDasharray="3 3" />
                                                        <circle cx={xPos + 18} cy="460" r="3" fill="#8b5cf6" />
                                                        <circle cx={xPos + 18} cy="280" r="2" fill="#8b5cf6" />
                                                    </g>
                                                )
                                            })}
                                        </g>
                                    )}

                                    {/* --- 5. Standard Title Block (Bottom Right) --- */}
                                    <g transform="translate(670, 480)">
                                        {/* Outer Box */}
                                        <rect x="0" y="0" width="200" height="50" fill="#ffffff" stroke="#0f172a" strokeWidth="1.5" />

                                        {/* Dividers */}
                                        <line x1="0" y1="25" x2="200" y2="25" stroke="#0f172a" strokeWidth="1" />
                                        <line x1="90" y1="25" x2="90" y2="50" stroke="#0f172a" strokeWidth="1" />

                                        {/* Top Row: Title */}
                                        <text x="8" y="16" fontSize="11" fontFamily="sans-serif" fontWeight="600" fill="#0f172a">
                                            Schematic Diagram
                                        </text>

                                        {/* Bottom Left: IP Rating */}
                                        <text x="8" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">IP Rating:</text>
                                        <text x="50" y="40" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                            {config.ipRating}
                                        </text>

                                        {/* Bottom Right: Control Type */}
                                        <text x="98" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">Control:</text>
                                        <text x="135" y="40" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                            {config.communication === 'No' ? 'Hardwired' : 'Network'}
                                        </text>
                                    </g>
                                </g>
                            </svg>
                        )}
                    </div>
                </section>
            </div>
        </div>
    )
}

export default BoosterSetPage
