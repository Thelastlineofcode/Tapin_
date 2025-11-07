import React, { useState } from 'react';

export default function EditListingForm({ listing, token, onClose, onUpdated }) {
  const [title, setTitle] = useState(listing.title);
  const [description, setDescription] = useState(listing.description || '');
  const [location, setLocation] = useState(listing.location || '');
  const [latitude, setLatitude] = useState(listing.latitude ?? '');
  const [longitude, setLongitude] = useState(listing.longitude ?? '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const body = { title, description, location };

      // Only include lat/lng if both are provided
      if (latitude && longitude) {
        body.latitude = parseFloat(latitude);
        body.longitude = parseFloat(longitude);
      }

      const res = await fetch(`http://127.0.0.1:5000/listings/${listing.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to update listing');
      }

      const updated = await res.json();
      if (onUpdated) onUpdated(updated);
      onClose();
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
          <h2>Edit Listing</h2>
          <button className="close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit} className="modal-body">
          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="edit-title">Title *</label>
            <input
              id="edit-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-description">Description</label>
            <textarea
              id="edit-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-location">Location</label>
            <input
              id="edit-location"
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </div>

          <details style={{ marginTop: '12px' }}>
            <summary style={{ cursor: 'pointer', marginBottom: '8px' }}>
              📍 Update map coordinates (optional)
            </summary>
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <div className="form-group" style={{ flex: 1, margin: 0 }}>
                <label htmlFor="edit-latitude">Latitude</label>
                <input
                  id="edit-latitude"
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="e.g., 37.7749"
                />
              </div>
              <div className="form-group" style={{ flex: 1, margin: 0 }}>
                <label htmlFor="edit-longitude">Longitude</label>
                <input
                  id="edit-longitude"
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="e.g., -122.4194"
                />
              </div>
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

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="cta" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
