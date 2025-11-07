import React, { useState } from 'react';

export default function ForgotPassword({ onClose, onSuccess }) {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!email) {
      setError('Email is required');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch('http://127.0.0.1:5000/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to send reset email');
      }

      setSent(true);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-card">
        <header className="modal-header">
          <h2>Reset Password</h2>
          <button className="close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        {!sent ? (
          <form onSubmit={handleSubmit} className="modal-body">
            <p>Enter your email address and we'll send you a link to reset your password.</p>

            {error && (
              <div className="error" role="alert">
                {error}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="reset-email">Email</label>
              <input
                id="reset-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className="form-actions">
              <button type="button" className="btn btn-secondary" onClick={onClose} disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary" disabled={loading}>
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
            </div>
          </form>
        ) : (
          <div className="modal-body">
            <div className="success" role="alert">
              ✓ If an account exists for {email}, a password reset link has been sent.
            </div>
            <p>Check your email for the reset link.</p>
            <button className="btn btn-primary" onClick={onClose} style={{ width: '100%' }}>
              Close
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
