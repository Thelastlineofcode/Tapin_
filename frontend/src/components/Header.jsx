import React from 'react';

export default function Header() {
  return (
    <header className="app-header">
      <div className="brand">
        <div>
          <h1>Tapin</h1>
          <p className="subtitle">Community Connections</p>
        </div>
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
