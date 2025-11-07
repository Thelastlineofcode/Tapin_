import React, { useState } from 'react';

export default function CreateListingForm({ token, onCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const body = { title, description, location };

      // Only include lat/lng if both are provided
      if (latitude && longitude) {
        body.latitude = parseFloat(latitude);
        body.longitude = parseFloat(longitude);
      }

      const res = await fetch('http://127.0.0.1:5000/listings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'create failed');
      setTitle('');
      setDescription('');
      setLocation('');
      setLatitude('');
      setLongitude('');
      onCreated && onCreated(data);
    } catch (error_) {
      setError(error_.message);
    }
  }

  return (
    <form onSubmit={submit} className="create-form">
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Title"
        required
      />
      <input
        value={location}
        onChange={(e) => setLocation(e.target.value)}
        placeholder="Location (e.g., San Francisco, CA)"
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description"
      />

      <div style={{ marginTop: '12px' }}>
        <details>
          <summary style={{ cursor: 'pointer', marginBottom: '8px' }}>
            📍 Add map coordinates (optional)
          </summary>
          <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
            <input
              type="number"
              step="any"
              value={latitude}
              onChange={(e) => setLatitude(e.target.value)}
              placeholder="Latitude (e.g., 37.7749)"
              style={{ flex: 1 }}
            />
            <input
              type="number"
              step="any"
              value={longitude}
              onChange={(e) => setLongitude(e.target.value)}
              placeholder="Longitude (e.g., -122.4194)"
              style={{ flex: 1 }}
            />
          </div>
          <small style={{ display: 'block', marginTop: '4px', color: '#666' }}>
            Tip: Use{' '}
            <a
              href="https://www.latlong.net/"
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: '#007bff' }}
            >
              latlong.net
            </a>{' '}
            to find coordinates
          </small>
        </details>
      </div>

      <div style={{ display: 'flex', gap: 8, marginTop: '12px' }}>
        <button type="submit" className="cta">
          Create Listing
        </button>
      </div>
      {error && <div className="error">{error}</div>}
    </form>
  );
}
