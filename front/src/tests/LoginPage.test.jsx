import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import LoginPage from '../pages/LoginPage';
import { AuthProvider } from '../context/AuthContext';

// Mock fetch globally
global.fetch = vi.fn();

describe('LoginPage', () => {
  it('renders login form properly', () => {
    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );
    
    expect(screen.getByPlaceholderText(/email or username/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('shows error on failed login', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      json: () => Promise.resolve({ detail: 'Invalid credentials' }),
    });

    render(
      <BrowserRouter>
        <AuthProvider>
          <LoginPage />
        </AuthProvider>
      </BrowserRouter>
    );

    fireEvent.change(screen.getByPlaceholderText(/email or username/i), { target: { value: 'wrong@test.com' } });
    fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'badpass' } });
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);

    const errorMsg = await screen.findByText(/invalid credentials/i);
    expect(errorMsg).toBeInTheDocument();
  });
});
