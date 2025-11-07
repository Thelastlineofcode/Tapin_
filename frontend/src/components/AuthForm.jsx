import React, { useState } from 'react';
import ForgotPassword from './ForgotPassword';

export default function AuthForm({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const endpoint = mode === 'login' ? '/login' : '/register';
      const res = await fetch(`http://127.0.0.1:5000${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.message || `HTTP ${res.status}`);
      }

      const data = await res.json();
      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="auth-form">
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="form-input"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="form-input"
          />

          {mode === 'register' && (
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="form-input"
            />
          )}

          {error && <p className="error" style={{ marginBottom: 'var(--space-3)' }}>{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '...' : mode === 'login' ? 'Login' : 'Register'}
          </button>

          {mode === 'login' && (
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="forgot-password-link"
            >
              Forgot Password?
            </button>
          )}
        </form>
      </div>

      {showForgotPassword && (
        <ForgotPassword
          onClose={() => setShowForgotPassword(false)}
          onSuccess={() => setShowForgotPassword(false)}
        />
      )}
    </>
  );
}
