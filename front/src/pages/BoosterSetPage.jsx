import { useState, useMemo, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import JSZip from 'jszip'
import './BoosterSetPage.css'

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
        {power && <text x="0" y="65" textAnchor="middle" fontSize="10" fill="#475569" fontFamily="monospace">{power} kW</text>}
    </g>
)

const StarterBlock = ({ x, y, type }) => {
    let symbol = null;
    if (type === 'VSD' || type === 'Variable Speed Drive') {
        symbol = (
            <g>
                <circle cx="0" cy="20" r="10" fill="none" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="14" x2="-4" y2="26" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="20" x2="4" y2="15" stroke="currentColor" strokeWidth="1" />
                <line x1="-4" y1="20" x2="4" y2="25" stroke="currentColor" strokeWidth="1" />
                <polygon points="1,24 5,26 4,22" fill="currentColor" />
            </g>
        )
    } else if (type === 'SS' || type === 'Soft Starter') {
        symbol = (
            <g>
                <line x1="-8" y1="20" x2="8" y2="20" stroke="currentColor" strokeWidth="1" />
                <polygon points="-4,15 4,20 -4,25" fill="none" stroke="currentColor" strokeWidth="1" />
                <line x1="4" y1="15" x2="4" y2="25" stroke="currentColor" strokeWidth="1" />
                <line x1="4" y1="25" x2="8" y2="28" stroke="currentColor" strokeWidth="1" />
            </g>
        )
    } else if (type === 'YD' || type === 'Star-Delta') {
        symbol = <text x="0" y="24" textAnchor="middle" fontSize="12" fill="currentColor">Y/Δ</text>
    } else if (type === '') {
        symbol = null;
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

const PLCBlock = ({ x, y }) => (
    <g transform={`translate(${x}, ${y})`}>
        <rect x="-30" y="0" width="60" height="40" fill="#f8fafc" stroke="currentColor" strokeWidth="1.5" />
        <text x="0" y="24" textAnchor="middle" fontSize="14" fontWeight="bold" fill="currentColor">PLC</text>
        <circle cx="-20" cy="40" r="1.5" fill="currentColor" />
        <circle cx="0" cy="40" r="1.5" fill="currentColor" />
        <circle cx="20" cy="40" r="1.5" fill="currentColor" />
    </g>
)

const SCADABlock = ({ x, y }) => (
    <g transform={`translate(${x}, ${y})`}>
        {/* Workstation base */}
        <line x1="-10" y1="35" x2="10" y2="35" stroke="currentColor" strokeWidth="2" />
        <line x1="0" y1="35" x2="0" y2="25" stroke="currentColor" strokeWidth="2" />
        {/* Screen */}
        <rect x="-25" y="0" width="50" height="30" rx="3" fill="#f8fafc" stroke="currentColor" strokeWidth="1.5" />
        <text x="0" y="19" textAnchor="middle" fontSize="10" fontWeight="bold" fill="currentColor">SCADA</text>
    </g>
)

function BoosterSetPage() {
    const navigate = useNavigate()
    const svgRef = useRef(null)

    const [config, setConfig] = useState({
        incomers: '1',
        pumps: '',
        motorStart: '',
        motorPower: '',
        ipRating: 'IP54',
        communication: '',
        plc: '',
        scada: '',
    })

    const [seriesList, setSeriesList] = useState([]);
    const [starterOptionsList, setStarterOptionsList] = useState([]);

    useEffect(() => {
        const fetchMasterData = async () => {
            try {
                const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
                const [seriesRes, startersRes] = await Promise.all([
                    fetch(`${apiUrl}/api/v1/series`),
                    fetch(`${apiUrl}/api/v1/starter-options`)
                ]);
                if (seriesRes.ok) setSeriesList(await seriesRes.json());
                if (startersRes.ok) setStarterOptionsList(await startersRes.json());
            } catch (error) {
                console.error("Failed to fetch master data", error);
            }
        };
        fetchMasterData();
    }, []);

    const dynamicMotorStartOptions = useMemo(() => seriesList.map(s => s.series_id), [seriesList]);
    const dynamicMotorPowerOptions = useMemo(() => {
        if (!config.motorStart) return [];
        // Filter starters by selected series, get unique power ratings, sort them
        const filtered = starterOptionsList.filter(s => s.series_id === config.motorStart);
        const uniquePowers = [...new Set(filtered.map(s => s.rated_load_power_kw))];
        return uniquePowers.sort((a, b) => a - b).map(p => String(p));
    }, [config.motorStart, starterOptionsList]);

    const CURRENT_CONFIG_OPTIONS = useMemo(() => ({
        pumps: { label: 'Number of Pumps', options: ['2', '3', '4'] },
        motorStart: {
            label: 'Type of Motor Start',
            options: dynamicMotorStartOptions,
        },
        motorPower: {
            label: 'Motor Power Rate (kW)',
            options: dynamicMotorPowerOptions,
        },
        communication: {
            label: 'Communication',
            options: ['No', 'ModbusTCP', 'ProfiNet'],
        },
        scada: {
            label: 'SCADA',
            options: ['No', 'YES'],
        },
        plc: {
            label: 'PLC',
            options: ['No', 'YES'],
        },
    }), [dynamicMotorStartOptions, dynamicMotorPowerOptions]);

    const [selectedAssets, setSelectedAssets] = useState(
        ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: false }), {})
    )

    const allFieldsFilled = useMemo(
        () => Object.values(config).every((v) => v !== ''),
        [config]
    )

    const handleConfigChange = (key, value) => {
        setConfig((prev) => {
            const nextConfig = { ...prev, [key]: value };
            // Auto-reset dependent downstream fields when parent changes
            if (key === 'motorStart') {
                nextConfig.motorPower = '';
            }
            return nextConfig;
        });
    }

    const toggleAsset = (asset) => {
        setSelectedAssets((prev) => ({ ...prev, [asset]: !prev[asset] }));
    };

    const selectAllAssets = () => {
        const newState = ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: true }), {});
        setSelectedAssets(newState);
    };

    const clearAllAssets = () => {
        const newState = ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: false }), {});
        setSelectedAssets(newState);
    };

    const handleDownload = async () => {
        try {
            // 1. Generate base64 PNG of the diagram FIRST for the backend Word Generator
            let b64diagram = null;
            let rawSvgData = null;
            if (svgRef.current) {
                rawSvgData = new XMLSerializer().serializeToString(svgRef.current);
                b64diagram = await new Promise((resolve) => {
                    const canvas = document.createElement("canvas");
                    canvas.width = 900;
                    canvas.height = 550;
                    const ctx = canvas.getContext("2d");
                    const img = new Image();
                    const svgBlob = new Blob([rawSvgData], { type: "image/svg+xml;charset=utf-8" });
                    const url = URL.createObjectURL(svgBlob);

                    img.onload = () => {
                        ctx.fillStyle = "white";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(img, 0, 0);
                        const dataURL = canvas.toDataURL("image/png");
                        URL.revokeObjectURL(url);
                        resolve(dataURL);
                    };

                    img.onerror = () => {
                        console.error("Failed to render SVG to PNG for backend");
                        URL.revokeObjectURL(url);
                        resolve(null);
                    };
                    img.src = url;
                });
            }

            const ats_included = config.incomers === '2';
            const requestPayload = {
                series_id: config.motorStart,
                motor_power_kw: parseFloat(config.motorPower),
                load_count: parseInt(config.pumps),
                ats_included: ats_included,
                communication: config.communication,
                plc_included: config.plc,
                scada_included: config.scada,
                selected_assets: Object.keys(selectedAssets).filter(k => selectedAssets[k]),
                single_line_diagram_b64: b64diagram
            };

            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/engine/generate-package`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload)
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                console.error("Engine generation failed:", errorData);
                alert("Failed to generate package. Valid configuration might not exist for these parameters.");
                return;
            }

            const backendZipBlob = await response.blob();
            // Load backend zip into JSZip to optionally append the UI Single Line Diagram
            const zip = await JSZip.loadAsync(backendZipBlob);

            if (rawSvgData) {
                zip.file("SingleLineDiagram.svg", rawSvgData);
                if (b64diagram) {
                    // Convert DataURL to Blob to inject back into local Zip
                    const base64Data = b64diagram.split(',')[1];
                    const byteCharacters = atob(base64Data);
                    const byteArrays = [];
                    for (let offset = 0; offset < byteCharacters.length; offset += 512) {
                        const slice = byteCharacters.slice(offset, offset + 512);
                        const byteNumbers = new Array(slice.length);
                        for (let i = 0; i < slice.length; i++) {
                            byteNumbers[i] = slice.charCodeAt(i);
                        }
                        byteArrays.push(new Uint8Array(byteNumbers));
                    }
                    const blob = new Blob(byteArrays, { type: 'image/png' });
                    zip.file("SingleLineDiagram.png", blob);
                }
            }

            const finalZipBlob = await zip.generateAsync({ type: "blob" })
            const url = URL.createObjectURL(finalZipBlob)
            const a = document.createElement('a')
            a.href = url
            a.download = `WaterBooster-${config.pumps}-Pumps-${config.motorPower}kW-Asset-Pack.zip`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
        } catch (e) {
            console.error("Error generating zip:", e)
            alert("An error occurred while generating the package.")
        }
    }

    const pumpCount = parseInt(config.pumps) || 0
    const incomerCount = parseInt(config.incomers) || 0

    const busYStart = 120;
    const busSpacing = 10;
    const busLines = [busYStart, busYStart + busSpacing, busYStart + busSpacing * 2, busYStart + busSpacing * 4]; // L1, L2, L3, PE(spaced extra)

    // Determine Title Block Control Text
    let controlText = 'Hardwired';
    if (config.scada && config.plc) controlText = 'SCADA + PLC';
    else if (config.scada) controlText = 'SCADA';
    else if (config.plc) controlText = 'PLC';
    else if (config.communication !== 'No' && config.communication !== '') controlText = 'Networked';

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
                            {Object.entries(CURRENT_CONFIG_OPTIONS).map(([key, { label, options }]) => (
                                <div className="booster__field" key={key}>
                                    <label className="booster__label" htmlFor={`config-${key}`}>
                                        {label}
                                    </label>
                                    <select
                                        id={`config-${key}`}
                                        className="booster__select"
                                        value={config[key]}
                                        onChange={(e) => handleConfigChange(key, e.target.value)}
                                        disabled={options.length === 0}
                                    >
                                        <option value="" disabled>
                                            {options.length === 0 ? "Pending..." : "Select…"}
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
                                incomers: '1',
                                pumps: '',
                                motorPower: '',
                                motorStart: '',
                                ipRating: 'IP54',
                                communication: '',
                                plc: '',
                                scada: ''
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
                                onClick={selectAllAssets}
                            >
                                Select All
                            </button>
                            <button
                                className="btn-secondary"
                                id="btn-clear-selection"
                                onClick={clearAllAssets}
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
                        {Object.entries(CURRENT_CONFIG_OPTIONS).map(([key, { label }]) => {
                            const value = config[key]
                            const hasFilled = value !== ''

                            let displayValue = value
                            if (key === 'motorPower' && value) displayValue = `${value} kW`
                            if (key === 'incomers' && value) displayValue = `${value} Incomer${value !== '1' ? 's' : ''}`
                            if (key === 'pumps' && value) displayValue = `${value} Pumps`
                            if (key === 'communication' && value == 'No') displayValue = 'Hardwired'
                            if (key === 'scada' && value) displayValue = `SCADA`
                            if (key === 'scada' && value == 'No') displayValue = `No SCADA`
                            if (key === 'plc' && value) displayValue = `PLC`
                            if (key === 'plc' && value == 'No') displayValue = `No PLC`

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
                                {Array.from({ length: 1 }).map((_, i) => {
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

                                {/* --- 3. Pump Feeders --- */}
                                {Array.from({ length: pumpCount || 2 }).map((_, i) => {
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

                                {/* --- 4. Control Logic (SCADA & PLC) --- */}
                                {config.scada && config.scada === 'YES' && (
                                    <g>
                                        <SCADABlock x={260} y={260} />
                                        {/* Connect SCADA to PLC or down to Comm Bus */}
                                        {config.plc && config.plc === 'YES' ? (
                                            <line x1="260" y1="295" x2="260" y2="360" stroke="#0ea5e9" strokeWidth="1.5" strokeDasharray="4 2" />
                                        ) : (
                                            <g>
                                                <line x1="260" y1="295" x2="260" y2="460" stroke="#0ea5e9" strokeWidth="1.5" strokeDasharray="4 2" />
                                                {(config.communication !== 'No' && config.communication !== '') && (
                                                    <circle cx="260" cy="460" r="3" fill="#8b5cf6" />
                                                )}
                                            </g>
                                        )}
                                        <text x="265" y="325" fontSize="8" fill="#0ea5e9" fontFamily="monospace">Ethernet</text>
                                    </g>
                                )}

                                {config.plc && config.plc === 'YES' && (
                                    <g>
                                        <PLCBlock x={260} y={360} />
                                        {/* Connect PLC to Comm Bus or draw Hardwired I/O Bus */}
                                        {(config.communication !== 'No' && config.communication !== '') ? (
                                            <g>
                                                <line x1="260" y1="400" x2="260" y2="460" stroke="#8b5cf6" strokeWidth="1.5" strokeDasharray="4 2" />
                                                <circle cx="260" cy="460" r="3" fill="#8b5cf6" />
                                            </g>
                                        ) : (
                                            <g>
                                                <line x1="260" y1="400" x2="260" y2="460" stroke="#64748b" strokeWidth="1.5" strokeDasharray="4 2" />
                                                <line x1="260" y1="460" x2="850" y2="460" stroke="#64748b" strokeWidth="1.5" strokeDasharray="4 2" />
                                                <text x="270" y="455" fontSize="10" fill="#64748b" fontFamily="monospace" fontWeight="bold">Hardwired I/O Bus</text>
                                                {Array.from({ length: pumpCount || 2 }).map((_, i) => {
                                                    const xPos = 400 + (i * 130);
                                                    return (
                                                        <g key={`hw-link-${i}`}>
                                                            <line x1={xPos + 18} y1="280" x2={xPos + 18} y2="460" stroke="#64748b" strokeWidth="1" strokeDasharray="4 2" />
                                                            <circle cx={xPos + 18} cy="460" r="2.5" fill="#64748b" />
                                                            <circle cx={xPos + 18} cy="280" r="2" fill="#64748b" />
                                                        </g>
                                                    )
                                                })}
                                            </g>
                                        )}
                                    </g>
                                )}

                                {/* --- 5. Communication Bus (Dashed Data Network) --- */}
                                {config.communication !== 'No' && config.communication !== '' && (
                                    <g>
                                        {/* Main Comm Bus Line */}
                                        <line x1="50" y1="460" x2="850" y2="460" stroke="#8b5cf6" strokeWidth="1.5" strokeDasharray="6 4" />
                                        <text x="60" y="455" fontSize="10" fill="#8b5cf6" fontFamily="monospace" fontWeight="bold">
                                            {config.communication} Network
                                        </text>

                                        {/* Connections from Comm Bus to each Starter */}
                                        {Array.from({ length: pumpCount || 2 }).map((_, i) => {
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

                                {/* --- 6. Standard Title Block (Bottom Right) --- */}
                                <g transform="translate(670, 480)">
                                    {/* Outer Box */}
                                    <rect x="0" y="0" width="200" height="70" fill="#ffffff" stroke="#0f172a" strokeWidth="1.5" />

                                    {/* Dividers */}
                                    <line x1="0" y1="25" x2="200" y2="25" stroke="#0f172a" strokeWidth="1" />
                                    <line x1="90" y1="25" x2="90" y2="75" stroke="#0f172a" strokeWidth="1" />
                                    <line x1="0" y1="48" x2="200" y2="48" stroke="#0f172a" strokeWidth="1" />

                                    {/* Top Row: Title */}
                                    <text x="8" y="16" fontSize="11" fontFamily="sans-serif" fontWeight="600" fill="#0f172a">
                                        Schematic Diagram
                                    </text>

                                    {/* Middle Left: IP Rating */}
                                    <text x="8" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">IP Rating:</text>
                                    <text x="50" y="38" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                        {config.ipRating}
                                    </text>

                                    {/* Middle Right: Control Type */}
                                    <text x="98" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">Control:</text>
                                    <text x="135" y="38" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                        {config.communication === 'No' ? 'Hardwired' : 'Network'}
                                    </text>
                                    {/* Bottom Left : SCADA */}
                                    <text x="8" y="60" fontSize="8" fill="#475569" fontFamily="sans-serif">SCADA:</text>
                                    <text x="50" y="60" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                        {config.scada ? 'Yes' : 'No'}
                                    </text>
                                    {/* Bottom Right : PLC */}
                                    <text x="98" y="60" fontSize="8" fill="#475569" fontFamily="sans-serif">PLC:</text>
                                    <text x="135" y="60" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">
                                        {config.plc ? 'Yes' : 'No'}
                                    </text>
                                </g>
                            </g>
                        </svg>
                    </div>
                </section>
            </div>
        </div>
    )
}

export default BoosterSetPage
