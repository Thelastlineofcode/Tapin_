import React, { useState } from 'react';
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function LoginForm({ onLogin, onForgotPassword, mode = 'login' }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const url = mode === 'login' ? `${API_URL}/login` : `${API_URL}/register`;
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'auth failed');
      onLogin && onLogin(data);
    } catch (error_) {
      setError(error_.message);
    }
  }

  return (
    <form onSubmit={submit} className="auth-form">
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        type="email"
        required
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        type="password"
        required
      />
      <button type="submit" className="chip">
        {mode === 'login' ? 'Login' : 'Register'}
      </button>
      {mode === 'login' && onForgotPassword && (
        <button
          type="button"
          className="link-button"
          onClick={onForgotPassword}
          style={{ fontSize: '0.85rem', marginTop: '4px' }}
        >
          Forgot Password?
        </button>
      )}
      {error && <div className="error">{error}</div>}
    </form>
  );
}
