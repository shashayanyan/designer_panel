import { render, screen, fireEvent, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import LoginPage from '../pages/LoginPage';
import { AuthProvider } from '../context/AuthContext';

// Mock fetch globally
global.fetch = vi.fn();

describe('LoginPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form properly', async () => {
    // Mock for AuthProvider mount
    fetch.mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'Not authenticated' }),
    });

    await act(async () => {
        render(
          <BrowserRouter>
            <AuthProvider>
              <LoginPage />
            </AuthProvider>
          </BrowserRouter>
        );
    });
    
    expect(screen.getByPlaceholderText(/username or email/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('shows error on failed login', async () => {
    // Mock for AuthProvider mount (first call to /me)
    fetch.mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Not authenticated' }),
    });
    
    // Mock for the login submission (second call to /login)
    fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Invalid credentials' }),
    });

    await act(async () => {
        render(
          <BrowserRouter>
            <AuthProvider>
              <LoginPage />
            </AuthProvider>
          </BrowserRouter>
        );
    });

    fireEvent.change(screen.getByPlaceholderText(/username or email/i), { target: { value: 'wrong@test.com' } });
    fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'badpass' } });
    
    const loginButton = screen.getByRole('button', { name: /sign in/i });
    
    await act(async () => {
        fireEvent.click(loginButton);
    });

    const errorMsg = await screen.findByText(/invalid credentials/i);
    expect(errorMsg).toBeInTheDocument();
  });
});
