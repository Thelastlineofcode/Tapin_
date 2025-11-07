import React from 'react';
import logoTransparent from '../../../Design-Assets/brand/logo-transparent.svg';

export default function DashboardLanding({ onEnter }) {
  return (
    <div className="landing-root">
      <div className="landing-hero">
        <img src={logoTransparent} alt="Tapin logo" className="landing-logo" />
        <h1 className="landing-title">Tapin — connect your community</h1>
        <p className="landing-sub">
          Find volunteer opportunities to give back, or discover local services from small
          businesses and professionals. One platform to strengthen your community.
        </p>

        <div className="landing-cta-row">
          <button className="btn btn-primary landing-cta" onClick={onEnter}>
            Explore opportunities
          </button>
          <button className="btn btn-outline landing-cta" onClick={onEnter}>
            Log in
          </button>
        </div>

        <ul className="landing-features">
          <li>🤝 Volunteer opportunities: Find meaningful ways to give back</li>
          <li>💼 Local services: Discover small businesses and professionals</li>
          <li>📍 Map view: Browse opportunities by location</li>
        </ul>

        <div className="landing-footer-note">Free to use • School Project</div>
      </div>
    </div>
  );
}
