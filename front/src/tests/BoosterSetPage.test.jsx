import { render, screen, fireEvent, act, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import BoosterSetPage from '../pages/BoosterSetPage'
import { AuthContext } from '../context/AuthContext'

// Mock navigate
const mockedNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => mockedNavigate,
    }
})

// Mock JSZip
vi.mock('jszip', () => {
    return {
        default: {
            loadAsync: vi.fn().mockResolvedValue({
                file: vi.fn(),
                generateAsync: vi.fn().mockResolvedValue(new Blob(['mock-zip'], { type: 'application/zip' }))
            })
        }
    }
})

// Mock fetch globally
global.fetch = vi.fn()

describe('BoosterSetPage', () => {
    const mockSeries = [
        { series_id: 'VFD', name: 'Variable Frequency Drive' },
        { series_id: 'DOL', name: 'Direct On Line' }
    ]
    const mockStarters = [
        { series_id: 'VFD', rated_load_power_kw: 30, starter_option_id: 'OPT-1' },
        { series_id: 'VFD', rated_load_power_kw: 15, starter_option_id: 'OPT-2' }
    ]

    beforeEach(() => {
        vi.clearAllMocks()
        // Mock initial master data fetch
        fetch.mockImplementation((url) => {
            if (url.includes('/api/v1/series')) {
                return Promise.resolve({ ok: true, json: () => Promise.resolve(mockSeries) })
            }
            if (url.includes('/api/v1/starter-options')) {
                return Promise.resolve({ ok: true, json: () => Promise.resolve(mockStarters) })
            }
            return Promise.resolve({ ok: true, blob: () => Promise.resolve(new Blob(['mock-blob'])) })
        })
    })

    it('renders the configuration panels', async () => {
        await act(async () => {
            render(
                <AuthContext.Provider value={{ token: 'mock-token', loading: false }}>
                    <BrowserRouter>
                        <BoosterSetPage />
                    </BrowserRouter>
                </AuthContext.Provider>
            )
        })
        expect(screen.getByText(/Configuration/i)).toBeInTheDocument()
        expect(screen.getByText(/Reference Architecture/i)).toBeInTheDocument()
    })

    it('submits the correct payload on download', async () => {
        await act(async () => {
            render(
                <AuthContext.Provider value={{ token: 'mock-token', loading: false }}>
                    <BrowserRouter>
                        <BoosterSetPage />
                    </BrowserRouter>
                </AuthContext.Provider>
            )
        })

        // 1. Fill the configuration
        // Select 3 Pumps
        fireEvent.change(screen.getByLabelText(/Number of Pumps/i), { target: { value: '3' } })
        
        // Select VFD
        fireEvent.change(screen.getByLabelText(/Type of Motor Start/i), { target: { value: 'VFD' } })
        
        // Wait for power options and select 30
        await waitFor(() => expect(screen.getByLabelText(/Motor Power Rate/i)).not.toBeDisabled())
        fireEvent.change(screen.getByLabelText(/Motor Power Rate/i), { target: { value: '30' } })
        
        // Select Communication: ModbusTCP
        fireEvent.change(screen.getByLabelText(/Communication/i), { target: { value: 'ModbusTCP' } })
        
        // Select SCADA: YES and PLC: YES
        fireEvent.change(screen.getByLabelText(/SCADA/i), { target: { value: 'YES' } })
        fireEvent.change(screen.getByLabelText(/PLC/i), { target: { value: 'YES' } })

        // 2. Select an asset
        fireEvent.click(screen.getByLabelText(/Bill of Materials/i))

        // 3. Trigger download
        const downloadButton = screen.getByRole('button', { name: /download package/i })
        
        // Assert button is enabled before clicking
        expect(downloadButton).not.toBeDisabled()

        await act(async () => {
            fireEvent.click(downloadButton)
        })

        // 4. Verify fetch call payload
        // The first 2 calls are for master data, the 3rd is the actual generate-package
        await waitFor(() => {
            const call = fetch.mock.calls.find(call => call[0].includes('generate-package'))
            expect(call).toBeDefined()
        })
        const payloadCall = fetch.mock.calls.find(call => call[0].includes('generate-package'))
        const payload = JSON.parse(payloadCall[1].body)

        expect(payload).toMatchObject({
            series_id: 'VFD',
            motor_power_kw: 30,
            load_count: 3,
            communication: 'ModbusTCP',
            plc_included: 'YES',
            scada_included: 'YES',
            selected_assets: expect.arrayContaining(['Bill of Materials'])
        })
    })

    it('handles hardwired case correctly in payload', async () => {
        await act(async () => {
            render(
                <AuthContext.Provider value={{ token: 'mock-token', loading: false }}>
                    <BrowserRouter>
                        <BoosterSetPage />
                    </BrowserRouter>
                </AuthContext.Provider>
            )
        })

        // Fill all required fields to enable the button
        fireEvent.change(screen.getByLabelText(/Number of Pumps/i), { target: { value: '2' } })
        fireEvent.change(screen.getByLabelText(/Type of Motor Start/i), { target: { value: 'VFD' } })
        await waitFor(() => expect(screen.getByLabelText(/Motor Power Rate/i)).not.toBeDisabled())
        fireEvent.change(screen.getByLabelText(/Motor Power Rate/i), { target: { value: '15' } })
        fireEvent.change(screen.getByLabelText(/PLC/i), { target: { value: 'No' } })
        fireEvent.change(screen.getByLabelText(/SCADA/i), { target: { value: 'No' } })
        
        // Specifically test the "No" (hardwired) case
        fireEvent.change(screen.getByLabelText(/Communication/i), { target: { value: 'No' } })
        
        const downloadButton = screen.getByRole('button', { name: /download package/i })
        expect(downloadButton).not.toBeDisabled()
        
        await act(async () => {
            fireEvent.click(downloadButton)
        })

        await waitFor(() => {
            const call = fetch.mock.calls.find(call => call[0].includes('generate-package'))
            expect(call).toBeDefined()
        })
        const payloadCall = fetch.mock.calls.find(call => call[0].includes('generate-package'))
        const payload = JSON.parse(payloadCall[1].body)

        expect(payload.communication).toBe('No')
    })
})
