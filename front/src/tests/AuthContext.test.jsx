import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AuthProvider, AuthContext } from '../context/AuthContext';
import { useEffect, useContext } from 'react';

// Test component that consumes context
const TestComponent = () => {
    const { user, token, login, logout } = useContext(AuthContext);
    
    return (
        <div>
            <span data-testid="user-role">{user ? user.role : 'null'}</span>
            <span data-testid="token-value">{token ? 'has-token' : 'no-token'}</span>
            <button onClick={() => login('mock_token_123', { role: 'User' })}>Login Test</button>
            <button onClick={logout}>Logout Test</button>
        </div>
    );
};

// Mock fetch for the /me endpoint
global.fetch = vi.fn();

describe('AuthContext', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('initializes with no token on load', () => {
        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );
        expect(screen.getByTestId('token-value').textContent).toBe('no-token');
    });

    it('login function sets token and fetches user', async () => {
        // Mock successful /me response for initial load
        fetch.mockResolvedValueOnce({
            ok: false
        });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        act(() => {
            screen.getByText('Login Test').click();
        });

        // Wait for user details to be set
        const userRole = await screen.findByText('User');
        expect(userRole).toBeInTheDocument();
        expect(screen.getByTestId('token-value').textContent).toBe('has-token');
    });
});
