import React from 'react';

export default function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div
        className="header-row"
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          alignItems: 'center',
        }}
      >
        <div className="brand" style={{ gridColumn: 2, justifySelf: 'center', textAlign: 'center' }}>
          <div>
            <h1>Tapin</h1>
            <p className="subtitle">Community Connections</p>
          </div>
        </div>

        {user && (
          <div
            className="header-actions"
            style={{ display: 'flex', alignItems: 'center', gap: 8, gridColumn: 3, justifySelf: 'end' }}
          >
            <span style={{ color: '#475569' }}>Hi, {user.email}</span>
            <button
              className="chip"
              onClick={() => {
                try { localStorage.removeItem('access_token'); } catch {}
                if (typeof onLogout === 'function') onLogout();
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>

      <div className="search-row">
        <input
          className="search"
          placeholder="Search volunteer opportunities, services, or location"
        />
      </div>
    </header>
  );
}
