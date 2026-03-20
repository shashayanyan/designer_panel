import { render, screen, act, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { AuthProvider, AuthContext } from '../context/AuthContext';
import { useContext } from 'react';

// Test component that consumes context
const TestComponent = () => {
    const { user, token, login, logout } = useContext(AuthContext);
    
    return (
        <div>
            <span data-testid="user-role">{user ? user.role : 'null'}</span>
            <span data-testid="token-value">{token ? 'has-token' : 'no-token'}</span>
            <button onClick={() => login('dummy_token', { role: 'User' })}>Login Test</button>
            <button onClick={logout}>Logout Test</button>
        </div>
    );
};

// Mock fetch for the /me endpoint
global.fetch = vi.fn();

describe('AuthContext', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        // Provide a default mock that returns not ok to avoid undefined errors
        fetch.mockResolvedValue({
            ok: false,
            json: () => Promise.resolve({ detail: 'Not authenticated' })
        });
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('initializes with no token on load', async () => {
        await act(async () => {
            render(
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            );
        });
        
        await waitFor(() => {
            expect(screen.getByTestId('token-value').textContent).toBe('no-token');
        });
    });

    it('login function sets token and user data', async () => {
        // Mock /me call on mount
        fetch.mockResolvedValueOnce({
            ok: false,
            json: () => Promise.resolve({ detail: 'Not authenticated' })
        });

        await act(async () => {
            render(
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            );
        });

        // Click login button - should call AuthContext.login
        await act(async () => {
            screen.getByText('Login Test').click();
        });

        // UI should reflect logged in state
        await waitFor(() => {
            expect(screen.getByTestId('user-role').textContent).toBe('User');
        });

        expect(screen.getByTestId('token-value').textContent).toBe('has-token');
    });

    it('logout function clears state', async () => {
        // Mock successful /me on mount (simulate already logged in)
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ username: 'testuser', role: 'User' })
        });
        // Mock for logout call
        fetch.mockResolvedValueOnce({ ok: true });

        await act(async () => {
            render(
                <AuthProvider>
                    <TestComponent />
                </AuthProvider>
            );
        });

        await waitFor(() => {
            expect(screen.getByTestId('user-role').textContent).toBe('User');
        });

        // Click logout
        await act(async () => {
            screen.getByText('Logout Test').click();
        });

        await waitFor(() => {
            expect(screen.getByTestId('user-role').textContent).toBe('null');
        });
        expect(screen.getByTestId('token-value').textContent).toBe('no-token');
    });
});
