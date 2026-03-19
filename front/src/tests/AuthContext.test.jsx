import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AuthProvider, useAuth } from '../context/AuthContext';
import { useEffect } from 'react';

// Test component that consumes context
const TestComponent = () => {
    const { user, token, login, logout } = useAuth();
    
    return (
        <div>
            <span data-testid="user-role">{user ? user.role : 'null'}</span>
            <span data-testid="token-value">{token ? 'has-token' : 'no-token'}</span>
            <button onClick={() => login('mock_token_123')}>Login Test</button>
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

    it('initializes with no token if not in storage', () => {
        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );
        expect(screen.getByTestId('token-value').textContent).toBe('no-token');
    });

    it('login function sets token and fetches user', async () => {
        // Mock successful /me response
        fetch.mockResolvedValueOnce({
            ok: true,
            json: () => Promise.resolve({ username: 'testuser', role: 'User' })
        });

        render(
            <AuthProvider>
                <TestComponent />
            </AuthProvider>
        );

        act(() => {
            screen.getByText('Login Test').click();
        });

        // The token is set and LocalStorage has it
        expect(localStorage.getItem('token')).toBe('mock_token_123');
        
        // Wait for user details to be fetched
        const userRole = await screen.findByText('User');
        expect(userRole).toBeInTheDocument();
    });
});
