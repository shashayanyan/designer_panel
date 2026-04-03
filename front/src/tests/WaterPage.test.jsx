import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import WaterPage from '../pages/WaterPage'

const mockedNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
    const actual = await vi.importActual('react-router-dom')
    return {
        ...actual,
        useNavigate: () => mockedNavigate,
    }
})

describe('WaterPage', () => {
    it('renders the application grid correctly', () => {
        render(
            <BrowserRouter>
                <WaterPage />
            </BrowserRouter>
        )
        expect(screen.getByText(/Choose an Application/i)).toBeInTheDocument()
        expect(screen.getByText(/Booster Set/i)).toBeInTheDocument()
        expect(screen.getByText(/Single Pump/i)).toBeInTheDocument()
    })

    it('navigates to booster set page when clicking the Booster Set card', () => {
        render(
            <BrowserRouter>
                <WaterPage />
            </BrowserRouter>
        )
        const boosterCard = screen.getByText(/Booster Set/i).closest('button')
        fireEvent.click(boosterCard)
        expect(mockedNavigate).toHaveBeenCalledWith('/water/booster-set')
    })

    it('does not navigate when clicking a disabled card', () => {
        render(
            <BrowserRouter>
                <WaterPage />
            </BrowserRouter>
        )
        const disabledCard = screen.getByText(/Single Pump/i).closest('button')
        expect(disabledCard).toBeDisabled()
        fireEvent.click(disabledCard)
        expect(mockedNavigate).not.toHaveBeenCalledWith('/water/single-pump')
    })
})
