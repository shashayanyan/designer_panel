import { useState, useMemo, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import JSZip from 'jszip'
import './BoosterSetPage.css'

const ASSET_LIST = [
    'Data Sheet',
    'Multi Line Diagram',
    'Bill of Materials',
    'Drawings',
    'Specification',
    'BIM Object',
]

// --- SVG Symbol Components (For Multi-Line) ---
const CircuitBreaker = ({ x, y, label }) => (
    <g transform={`translate(${x}, ${y})`}>
        <text x="25" y="15" fontSize="10" fill="#475569" fontFamily="monospace">{label}</text>
        <line x1="-10" y1="0" x2="-5" y2="20" stroke="currentColor" strokeWidth="1.5" />
        <line x1="0" y1="0" x2="5" y2="20" stroke="currentColor" strokeWidth="1.5" />
        <line x1="10" y1="0" x2="15" y2="20" stroke="currentColor" strokeWidth="1.5" />
        <line x1="-8" y1="10" x2="12" y2="10" stroke="currentColor" strokeWidth="2" strokeDasharray="2 2" />
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

const MotorImage = ({ x, y, label, power }) => (
    <g transform={`translate(${x}, ${y})`}>
        <circle cx="0" cy="20" r="26" fill="white" stroke="#3f9242ff" strokeWidth="2" />
        <text x="0" y="24" textAnchor="middle" fontSize="12" fontFamily="sans-serif" fill="#3f9242ff">M</text>
        <text x="0" y="50" textAnchor="middle" fontSize="10" fill="#3f9242ff" fontFamily="monospace">{label}</text>
        {power && <text x="0" y="65" textAnchor="middle" fontSize="10" fill="#3f9242ff" fontFamily="monospace">{power} kW</text>}
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
        <rect x="-40" y="0" width="80" height="40" fill="#f8fafc" stroke="currentColor" strokeWidth="1.5" />
        <text x="0" y="24" textAnchor="middle" fontSize="14" fontWeight="bold" fill="currentColor">PLC</text>
        <circle cx="-20" cy="40" r="1.5" fill="currentColor" />
        <circle cx="0" cy="40" r="1.5" fill="currentColor" />
        <circle cx="20" cy="40" r="1.5" fill="currentColor" />
    </g>
)

const SCADABlock = ({ x, y }) => (
    <g transform={`translate(${x}, ${y})`}>
        <line x1="-10" y1="35" x2="10" y2="35" stroke="currentColor" strokeWidth="2" />
        <line x1="0" y1="35" x2="0" y2="25" stroke="currentColor" strokeWidth="2" />
        <rect x="-25" y="0" width="50" height="30" rx="3" fill="#f8fafc" stroke="currentColor" strokeWidth="1.5" />
        <text x="0" y="19" textAnchor="middle" fontSize="10" fontWeight="bold" fill="currentColor">SCADA</text>
    </g>
)

const NetworkCloud = ({ x, y }) => (
    <g transform={`translate(${x}, ${y})`}>
        <rect x="-50" y="0" width="100" height="40" rx="8" fill="#f1f5f9" stroke="#94a3b8" strokeWidth="2" />
        <text x="0" y="24" textAnchor="middle" fontSize="12" fontWeight="bold" fill="#64748b">Remote Net</text>
    </g>
)

// --- Image Selection Helper for Physical Architecture ---
const getStarterImage = (motorStart, power) => {
    if (!motorStart) return '';
    if (motorStart === 'DOL') return '/images/booster-set/Direct-On-Line.png';

    const kw = parseFloat(power);
    //if (!kw) return '/images/booster-set/VSD-front.png';
    if (motorStart === 'VSD') return '/images/booster-set/VSD-front.png';

    if (kw <= 4) return '/images/booster-set/ATV600_0.75-4kW.png';
    if (kw <= 5.5) return '/images/booster-set/ATV600_5.5kW.png';
    if (kw <= 11) return '/images/booster-set/ATV600_7.5-11kW.png';
    if (kw <= 22.5) return '/images/booster-set/ATV600_15-22kW.png';
    if (kw <= 45) return '/images/booster-set/ATV600_30-45kW.png';
    return '/images/booster-set/ATV600_55-75kW.png';
}

const getStarterImage2 = (motorStart, power) => {
    if (!motorStart) return '';
    const kw = parseFloat(power);
    let powerRange = '0.11';
    if (motorStart === 'DOL') {
        if (kw >= 45.0) powerRange = '45.0';
        else if (kw >= 37.0) powerRange = '37.0';
        else if (kw >= 30) powerRange = '30.0';
        else if (kw >= 18.5) powerRange = '18.5';
        else if (kw >= 15) powerRange = '15.0';
        else if (kw >= 5.5) powerRange = '5.5';
        return '/images/motor-starts/LC1D/LC1D-' + powerRange + 'kW.png';
    }
    else if (motorStart === 'SS') {
        powerRange = '0.37';
        if (kw >= 55) powerRange = '55.0';
        else if (kw >= 45) powerRange = '45.0';
        else if (kw >= 37) powerRange = '37.0';
        else if (kw >= 30) powerRange = '30.0';
        else if (kw >= 22) powerRange = '22.0';
        else if (kw >= 18.5) powerRange = '18.5';
        else if (kw >= 15) powerRange = '15.0';
        else if (kw >= 7.5) powerRange = '7.5';
        else if (kw >= 5.5) powerRange = '5.5';
        else if (kw >= 4) powerRange = '4.0';
        else if (kw >= 1.5) powerRange = '1.5';
        return '/images/motor-starts/ATS/ATS-' + powerRange + 'kW.jpg';
    } else if (motorStart === 'VSD') {
        return '/images/motor-starts/ATV/ATV-' + kw + 'kW.jpg';
    }
    return '/images/motor-starts/LC1D/LC1D-0.11kW.png';
}

function BoosterSetPage() {
    const navigate = useNavigate()
    const multiLineRef = useRef(null)
    const refArchRef = useRef(null)

    const [config, setConfig] = useState({
        incomers: '1', pumps: '', motorStart: '', motorPower: '', ipRating: 'IP54', communication: '', plc: '', scada: '',
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
        const filtered = starterOptionsList.filter(s => s.series_id === config.motorStart);
        const uniquePowers = [...new Set(filtered.map(s => s.rated_load_power_kw))];
        return uniquePowers.sort((a, b) => a - b).map(p => String(p));
    }, [config.motorStart, starterOptionsList]);

    const CURRENT_CONFIG_OPTIONS = useMemo(() => ({
        pumps: { label: 'Number of Pumps', options: ['2', '3', '4'] },
        motorStart: { label: 'Type of Motor Start', options: dynamicMotorStartOptions },
        motorPower: { label: 'Motor Power Rate (kW)', options: dynamicMotorPowerOptions },
        communication: { label: 'Communication', options: ['No', 'ModbusTCP', 'ProfiNet'] },
        scada: { label: 'SCADA', options: ['No', 'YES'] },
        plc: { label: 'PLC', options: ['No', 'YES'] },
    }), [dynamicMotorStartOptions, dynamicMotorPowerOptions]);

    const [selectedAssets, setSelectedAssets] = useState(
        ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: false }), {})
    )

    const allFieldsFilled = useMemo(() => Object.values(config).every((v) => v !== ''), [config])

    const handleConfigChange = (key, value) => {
        setConfig((prev) => {
            const nextConfig = { ...prev, [key]: value };
            if (key === 'motorStart') nextConfig.motorPower = '';
            return nextConfig;
        });
    }

    const toggleAsset = (asset) => setSelectedAssets((prev) => ({ ...prev, [asset]: !prev[asset] }));
    const selectAllAssets = () => setSelectedAssets(ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: true }), {}));
    const clearAllAssets = () => setSelectedAssets(ASSET_LIST.reduce((acc, a) => ({ ...acc, [a]: false }), {}));
    const numberIn3Digits = (num) => {
        return num.toString().padStart(3, '0');
    }
    const handleDownload = async () => {
        try {
            const renderSvgToPng = async (svgElement) => {
                if (!svgElement) return { dataURL: null, rawSvgData: null };

                // 1. Clone the SVG so we don't manipulate the live UI
                const clone = svgElement.cloneNode(true);

                // 2. Find all images and convert them to Base64 Data URIs
                const images = clone.querySelectorAll('image');
                for (let img of images) {
                    const href = img.getAttribute('href');
                    // Only fetch if it isn't already a data URI
                    if (href && !href.startsWith('data:')) {
                        try {
                            const response = await fetch(href);
                            const blob = await response.blob();
                            const base64 = await new Promise((resolve) => {
                                const reader = new FileReader();
                                reader.onloadend = () => resolve(reader.result);
                                reader.readAsDataURL(blob);
                            });
                            // Inject the Base64 string directly into the SVG image tag
                            img.setAttribute('href', base64);
                        } catch (err) {
                            console.error(`Failed to inline image: ${href}`, err);
                        }
                    }
                }

                // 3. Serialize the Base64-embedded SVG
                const rawSvgData = new XMLSerializer().serializeToString(clone);

                return new Promise((resolve) => {
                    const canvas = document.createElement("canvas");
                    canvas.width = 900;
                    canvas.height = 600;
                    const ctx = canvas.getContext("2d");
                    const img = new Image();

                    img.crossOrigin = "Anonymous";

                    const svgBlob = new Blob([rawSvgData], { type: "image/svg+xml;charset=utf-8" });
                    const url = URL.createObjectURL(svgBlob);

                    img.onload = () => {
                        ctx.fillStyle = "white";
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.drawImage(img, 0, 0);
                        const dataURL = canvas.toDataURL("image/png");
                        URL.revokeObjectURL(url);
                        // Return the fully embedded SVG data alongside the PNG
                        resolve({ dataURL, rawSvgData });
                    };
                    img.onerror = () => {
                        console.error("Failed to render SVG to PNG");
                        URL.revokeObjectURL(url);
                        resolve({ dataURL: null, rawSvgData });
                    };
                    img.src = url;
                });
            };

            const multiLineResult = await renderSvgToPng(multiLineRef.current);
            const refArchResult = await renderSvgToPng(refArchRef.current);

            let b64diagram = multiLineResult.dataURL;
            let rawSvgData = multiLineResult.rawSvgData;

            const requestPayload = {
                series_id: config.motorStart,
                motor_power_kw: parseFloat(config.motorPower),
                load_count: parseInt(config.pumps),
                ats_included: config.incomers === '2',
                communication: config.communication,
                plc_included: config.plc,
                scada_included: config.scada,
                selected_assets: Object.keys(selectedAssets).filter(k => selectedAssets[k]),
                multi_line_diagram_b64: b64diagram
            };

            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/v1/engine/generate-package`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestPayload)
            });

            if (!response.ok) {
                alert("Failed to generate package. Valid configuration might not exist for these parameters.");
                return;
            }

            const backendZipBlob = await response.blob();
            const zip = await JSZip.loadAsync(backendZipBlob);

            const addDataUrlToZip = (zipObj, filename, dataUrl) => {
                if (!dataUrl) return;
                const base64Data = dataUrl.split(',')[1];
                const byteCharacters = atob(base64Data);
                const byteArrays = [];
                for (let offset = 0; offset < byteCharacters.length; offset += 512) {
                    const slice = byteCharacters.slice(offset, offset + 512);
                    const byteNumbers = new Array(slice.length);
                    for (let i = 0; i < slice.length; i++) byteNumbers[i] = slice.charCodeAt(i);
                    byteArrays.push(new Uint8Array(byteNumbers));
                }
                zipObj.file(filename, new Blob(byteArrays, { type: 'image/png' }));
            };
            // put images only if they are selected, with calculated index
            if (selectedAssets['Multi Line Diagram']) {
                let assetIndex = 4;
                if (selectedAssets['Data Sheet']) {
                    assetIndex = 10;
                }

                if (rawSvgData) zip.file(`${numberIn3Digits(assetIndex)}_MultiLineDiagram.svg`, rawSvgData);
                assetIndex++;
                addDataUrlToZip(zip, `${numberIn3Digits(assetIndex)}_MultiLineDiagram.png`, b64diagram);
                assetIndex++;
                //if (refArchResult.rawSvgData) zip.file("013_ReferenceArchitecture.svg", refArchResult.rawSvgData);
                addDataUrlToZip(zip, `${numberIn3Digits(assetIndex)}_ReferenceArchitecture.png`, refArchResult.dataURL);

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

    // Logic Variables
    const pumpCount = parseInt(config.pumps) || 0;
    const busYStart = 120;
    const busSpacing = 10;
    const busLines = [busYStart, busYStart + busSpacing, busYStart + busSpacing * 2, busYStart + busSpacing * 4];

    // Control Architecture Flags
    const hasSCADA = config.scada === 'YES';
    const hasPLC = config.plc === 'YES';
    const hasComms = config.communication !== 'No' && config.communication !== '';

    let controlText = 'Hardwired';
    if (hasSCADA && hasPLC) controlText = 'SCADA + PLC';
    else if (hasSCADA) controlText = 'SCADA';
    else if (hasPLC) controlText = 'PLC';
    else if (hasComms) controlText = 'Networked';

    return (
        <div className="booster">
            <header className="booster__header fade-in">
                <div className="booster__header-left">
                    <h1 className="booster__title">Motor Control Asset Library</h1>
                    <p className="booster__subtitle">Configure your booster set parameters and download the asset package.</p>
                </div>
                <div className="booster__header-right">
                    <button className="btn-secondary" onClick={() => navigate('/water')}>← Back to Water Apps</button>
                    <button className="btn-secondary" onClick={() => navigate('/')}>← Back to Home</button>
                </div>
            </header>

            <div className="booster__body">
                <aside className="booster__sidebar">
                    <section className="booster__config glass-card fade-in fade-in-delay-1">
                        <h2 className="booster__section-title">Configuration</h2>
                        <div className="booster__fields">
                            {Object.entries(CURRENT_CONFIG_OPTIONS).map(([key, { label, options }]) => (
                                <div className="booster__field" key={key}>
                                    <label className="booster__label" htmlFor={`config-${key}`}>{label}</label>
                                    <select
                                        id={`config-${key}`}
                                        className="booster__select"
                                        value={config[key]}
                                        onChange={(e) => handleConfigChange(key, e.target.value)}
                                        disabled={options.length === 0}
                                    >
                                        <option value="" disabled>{options.length === 0 ? "Pending..." : "Select…"}</option>
                                        {options.map((opt) => (
                                            <option key={opt} value={opt}>{opt}{key === 'motorPower' ? ' kW' : ''}</option>
                                        ))}
                                    </select>
                                </div>
                            ))}
                        </div>
                        <button
                            className="btn-reset"
                            style={{ marginTop: 'var(--space-md)', width: '100%' }}
                            onClick={() => setConfig({ incomers: '1', pumps: '', motorPower: '', motorStart: '', ipRating: 'IP54', communication: '', plc: '', scada: '' })}
                        >
                            Reset
                        </button>
                    </section>

                    <section className="booster__assets glass-card fade-in fade-in-delay-3">
                        <h2 className="booster__section-title">Assets</h2>
                        <div className="booster__asset-buttons">
                            <button className="btn-secondary" onClick={selectAllAssets}>Select All</button>
                            <button className="btn-secondary" onClick={clearAllAssets}>Clear All</button>
                        </div>
                        <div className="booster__checklist">
                            {ASSET_LIST.map((asset) => (
                                <label className="booster__check-item" key={asset}>
                                    <input type="checkbox" checked={selectedAssets[asset]} onChange={() => toggleAsset(asset)} className="booster__checkbox" />
                                    <span className="booster__check-label">{asset}</span>
                                </label>
                            ))}
                        </div>
                        <button className="btn-primary booster__download-btn" disabled={!allFieldsFilled} onClick={handleDownload}>
                            <span>📦</span> Download Package
                        </button>
                    </section>
                </aside>

                <div className="booster__diagrams-container" style={{ display: 'flex', flexDirection: 'column', gap: '2rem', flex: 1 }}>

                    {/* ─── Diagram 1: Multi-Line Electrical Diagram ─── */}
                    <section className="booster__diagram glass-card fade-in fade-in-delay-2">
                        <h2 className="booster__section-title">Multi-Line Diagram</h2>
                        <div className="booster__diagram-canvas">
                            <svg ref={multiLineRef} viewBox="0 0 900 550" xmlns="http://www.w3.org/2000/svg" style={{ width: '80%', minWidth: '600px', backgroundColor: 'white', borderRadius: '8px' }}>
                                <g stroke="#0f172a" fill="#0f172a">
                                    <line x1="50" y1={busLines[0]} x2="850" y2={busLines[0]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[1]} x2="850" y2={busLines[1]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[2]} x2="850" y2={busLines[2]} strokeWidth="2" />
                                    <line x1="50" y1={busLines[3]} x2="850" y2={busLines[3]} strokeWidth="2" strokeDasharray="8 4" stroke="#16a34a" />

                                    <text x="30" y={busLines[0] + 4} fontSize="10" fontFamily="monospace">L1</text>
                                    <text x="30" y={busLines[1] + 4} fontSize="10" fontFamily="monospace">L2</text>
                                    <text x="30" y={busLines[2] + 4} fontSize="10" fontFamily="monospace">L3</text>
                                    <text x="30" y={busLines[3] + 4} fontSize="10" fontFamily="monospace" fill="#16a34a">PE</text>

                                    {/* Incomer Logic */}
                                    <g>
                                        <line x1="110" y1="40" x2="110" y2="60" strokeWidth="1.5" />
                                        <line x1="120" y1="40" x2="120" y2="60" strokeWidth="1.5" />
                                        <line x1="130" y1="40" x2="130" y2="60" strokeWidth="1.5" />
                                        <CircuitBreaker x={120} y={60} label="QF1" />
                                        <line x1="110" y1="90" x2="110" y2={busLines[0]} strokeWidth="1.5" />
                                        <line x1="120" y1="90" x2="120" y2={busLines[1]} strokeWidth="1.5" />
                                        <line x1="130" y1="90" x2="130" y2={busLines[2]} strokeWidth="1.5" />
                                        <circle cx="110" cy={busLines[0]} r="3" />
                                        <circle cx="120" cy={busLines[1]} r="3" />
                                        <circle cx="130" cy={busLines[2]} r="3" />
                                    </g>

                                    {/* Pumps Feeder Logic */}
                                    {Array.from({ length: pumpCount || 2 }).map((_, i) => {
                                        const xPos = 400 + (i * 130);
                                        return (
                                            <g key={`pump-${i}`}>
                                                <circle cx={xPos - 10} cy={busLines[0]} r="3" />
                                                <circle cx={xPos} cy={busLines[1]} r="3" />
                                                <circle cx={xPos + 10} cy={busLines[2]} r="3" />
                                                <line x1={xPos - 10} y1={busLines[0]} x2={xPos - 10} y2="200" strokeWidth="1.5" />
                                                <line x1={xPos} y1={busLines[1]} x2={xPos} y2="200" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1={busLines[2]} x2={xPos + 10} y2="200" strokeWidth="1.5" />
                                                <CircuitBreaker x={xPos} y={200} label={`QM${i + 1}`} />
                                                <line x1={xPos - 10} y1="230" x2={xPos - 10} y2="260" strokeWidth="1.5" />
                                                <line x1={xPos} y1="230" x2={xPos} y2="260" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="230" x2={xPos + 10} y2="260" strokeWidth="1.5" />
                                                <StarterBlock x={xPos} y={260} type={config.motorStart} />
                                                <line x1={xPos - 10} y1="300" x2={xPos - 10} y2="340" strokeWidth="1.5" />
                                                <line x1={xPos} y1="300" x2={xPos} y2="340" strokeWidth="1.5" />
                                                <line x1={xPos + 10} y1="300" x2={xPos + 10} y2="340" strokeWidth="1.5" />
                                                <MotorSymbol x={xPos} y={340} label={`Pump ${i + 1}`} power={config.motorPower} />
                                                <line x1={xPos - 16} y1={360} x2={xPos - 30} y2={360} stroke="#16a34a" strokeWidth="1.5" />
                                                <line x1={xPos - 30} y1={360} x2={xPos - 30} y2={busLines[3]} stroke="#16a34a" strokeWidth="1.5" strokeDasharray="4 2" />
                                                <circle cx={xPos - 30} cy={busLines[3]} r="3" fill="#16a34a" />
                                            </g>
                                        )
                                    })}

                                    {/* --- Logic: SCADA & PLC --- */}
                                    {hasSCADA && (
                                        <g>
                                            <SCADABlock x={260} y={260} />
                                            {hasPLC ? (
                                                <line x1="260" y1="295" x2="260" y2="360" stroke="#0ea5e9" strokeWidth="1.5" strokeDasharray="4 2" />
                                            ) : (
                                                <g>
                                                    <line x1="260" y1="295" x2="260" y2="460" stroke="#0ea5e9" strokeWidth="1.5" strokeDasharray="4 2" />
                                                    {hasComms && <circle cx="260" cy="460" r="3" fill="#8b5cf6" />}
                                                </g>
                                            )}
                                            <text x="265" y="325" fontSize="8" fill="#0ea5e9" fontFamily="monospace">Ethernet</text>
                                        </g>
                                    )}

                                    {hasPLC && (
                                        <g>
                                            <PLCBlock x={260} y={360} />
                                            {hasComms ? (
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

                                    {/* --- Communication Bus --- */}
                                    {hasComms && (
                                        <g>
                                            <line x1="50" y1="460" x2="850" y2="460" stroke="#8b5cf6" strokeWidth="1.5" strokeDasharray="6 4" />
                                            <text x="60" y="455" fontSize="10" fill="#8b5cf6" fontFamily="monospace" fontWeight="bold">{config.communication} Network</text>
                                            {Array.from({ length: pumpCount || 2 }).map((_, i) => {
                                                const xPos = 400 + (i * 130);
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

                                    {/* --- Standard Title Block (Bottom Right) --- */}
                                    <g transform="translate(670, 480)">
                                        <rect x="0" y="0" width="200" height="70" fill="#ffffff" stroke="#0f172a" strokeWidth="1.5" />
                                        <line x1="0" y1="25" x2="200" y2="25" stroke="#0f172a" strokeWidth="1" />
                                        <line x1="90" y1="25" x2="90" y2="75" stroke="#0f172a" strokeWidth="1" />
                                        <line x1="0" y1="48" x2="200" y2="48" stroke="#0f172a" strokeWidth="1" />
                                        <text x="8" y="16" fontSize="11" fontFamily="sans-serif" fontWeight="600" fill="#0f172a">Schematic Diagram</text>
                                        <text x="8" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">IP Rating:</text>
                                        <text x="50" y="38" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">{config.ipRating}</text>
                                        <text x="98" y="38" fontSize="8" fill="#475569" fontFamily="sans-serif">Comms:</text>
                                        <text x="135" y="38" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">{config.communication !== 'No' ? config.communication : 'Hardwired'}</text>
                                        <text x="8" y="60" fontSize="8" fill="#475569" fontFamily="sans-serif">SCADA:</text>
                                        <text x="50" y="60" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">{config.scada ? 'Yes' : 'No'}</text>
                                        <text x="98" y="60" fontSize="8" fill="#475569" fontFamily="sans-serif">PLC:</text>
                                        <text x="135" y="60" fontSize="10" fontWeight="bold" fill="#0f172a" fontFamily="sans-serif">{config.plc ? 'Yes' : 'No'}</text>
                                    </g>
                                </g>
                            </svg>
                        </div>
                    </section>

                    {/* ─── Diagram 2: Reference Architecture (Images) ─── */}
                    <section className="booster__diagram glass-card fade-in fade-in-delay-3">
                        <h2 className="booster__section-title">Reference Architecture</h2>
                        <div className="booster__diagram-canvas">
                            <svg ref={refArchRef} viewBox="0 0 900 600" xmlns="http://www.w3.org/2000/svg" style={{ width: '80%', minWidth: '600px', backgroundColor: '#f8fafc', borderRadius: '8px' }}>

                                <g stroke="#0f172a" strokeWidth="2">
                                    {/* Super Level Routing (SCADA/Remote -> PLC/Bus) */}
                                    {hasSCADA && (
                                        hasPLC ? (
                                            <path d="M 450 110 L 450 170" stroke="#0ea5e9" strokeWidth="3" fill="none" strokeDasharray="6 4" />
                                        ) : (
                                            hasComms ? (
                                                <path d="M 450 110 L 450 280" stroke="#0ea5e9" strokeWidth="3" fill="none" strokeDasharray="6 4" />
                                            ) : null // SCADA with no PLC and no Comms is illogical, omit connection.
                                        )
                                    )}

                                    {/* Remote Comms Dropdown (If Comms but no local PLC/SCADA) */}
                                    {!hasSCADA && !hasPLC && hasComms && (
                                        <path d="M 450 120 L 450 280" stroke="#8b5cf6" strokeWidth="3" fill="none" />
                                    )}

                                    {/* PLC to Control Bus */}
                                    {hasPLC && (hasComms || true) && (
                                        <path d="M 450 250 L 450 280" stroke={hasComms ? "#8b5cf6" : "#64748b"} strokeWidth="3" fill="none" />
                                    )}

                                    {/* Main Control Bus (Horizontal) */}
                                    {(hasSCADA || hasPLC || hasComms) && (
                                        <>
                                            <line x1="140" y1="280" x2="760" y2="280" stroke={hasComms ? "#8b5cf6" : "#64748b"} strokeWidth="3" strokeDasharray={hasComms ? "" : "6 4"} />
                                            <text x="210" y="270" fill={hasComms ? "#8b5cf6" : "#64748b"} fontSize="14">
                                                {hasComms ? `${config.communication} Bus` : "Hardwired I/O Bus"}
                                            </text>
                                        </>
                                    )}

                                    {/* Control Drop Downs & Power Lines to Pumps */}
                                    {Array.from({ length: pumpCount || 2 }).map((_, i) => {
                                        const totalWidth = 600;
                                        const startX = 450 - (totalWidth / 2);
                                        const step = totalWidth / ((pumpCount || 2) - 1 || 1);
                                        const xPos = pumpCount === 1 ? 450 : startX + (i * step);

                                        return (
                                            <g key={`physical-link-${i}`}>
                                                {/* Control Bus to Starter Drop Line */}
                                                {(hasSCADA || hasPLC || hasComms) && (
                                                    <line x1={xPos} y1="280" x2={xPos} y2="340" stroke={hasComms ? "#8b5cf6" : "#64748b"} strokeWidth="2" strokeDasharray={hasComms ? "" : "4 2"} />
                                                )}

                                                {/* Power Line from Starter to Pump */}
                                                <line x1={xPos} y1="440" x2={xPos} y2="480" stroke="#334155" strokeWidth="4" />
                                            </g>
                                        )
                                    })}
                                </g>

                                {/* Physical Device Images */}

                                {/* SCADA Image */}
                                {hasSCADA && (
                                    <image href="/images/booster-set/SCADA.png" x="400" y="30" width="100" height="80" preserveAspectRatio="xMidYMid meet" />
                                )}

                                {/* Remote Network Gateway (If Comms only) */}
                                {!hasSCADA && !hasPLC && hasComms && (
                                    <NetworkCloud x={450} y={80} />
                                )}

                                {/* PLC Image */}
                                {hasPLC && (
                                    <image href="/images/booster-set/M262.jpg" x="400" y="170" width="100" height="80" preserveAspectRatio="xMidYMid meet" />
                                )}
                                {hasPLC && (
                                    <text x="380" y="210" textAnchor='middle' fontSize="12" fontWeight="bold">PLC</text>
                                )}

                                {/* Starters & Pumps Loop */}
                                {Array.from({ length: pumpCount || 2 }).map((_, i) => {
                                    const totalWidth = 600;
                                    const startX = 450 - (totalWidth / 2);
                                    const step = totalWidth / ((pumpCount || 2) - 1 || 1);
                                    const xPos = pumpCount === 1 ? 450 : startX + (i * step);

                                    const starterImg = getStarterImage2(config.motorStart, config.motorPower);

                                    return (
                                        <g key={`physical-devices-${i}`}>
                                            {/* Starter Box Image (VSD or DOL) */}
                                            {config.motorStart && (
                                                <image href={starterImg} x={xPos - 35} y="340" width="70" height="100" preserveAspectRatio="xMidYMid meet" />
                                            )}

                                            {/* Pump Image */}
                                            {/* <image href="/images/booster-set/pump.png" x={xPos - 50} y="480" width="100" height="100" preserveAspectRatio="xMidYMid meet" /> */}
                                            <MotorImage x={xPos} y="480" width="200" height="200" />

                                            {/* Labels */}
                                            <text x={xPos} y="330" textAnchor="middle" fontSize="12" fontWeight="bold" fill="#334155">Starter {i + 1}</text>
                                            {/* <text x={xPos} y="590" textAnchor="middle" fontSize="12" fontWeight="bold" fill="#334155">Pump {i + 1}</text> */}
                                        </g>
                                    )
                                })}

                            </svg>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    )
}

export default BoosterSetPage