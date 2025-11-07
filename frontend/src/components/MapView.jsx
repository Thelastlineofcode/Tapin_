import React, { useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icons in React-Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function MapView({ listings, onListingClick }) {
  const mapRef = useRef();

  // Filter listings that have coordinates
  const mappableListings = listings.filter(
    (listing) => listing.latitude != null && listing.longitude != null,
  );

  // Calculate center: average of all listing coordinates or default
  const center =
    mappableListings.length > 0
      ? [
          mappableListings.reduce((sum, l) => sum + l.latitude, 0) / mappableListings.length,
          mappableListings.reduce((sum, l) => sum + l.longitude, 0) / mappableListings.length,
        ]
      : [37.7749, -122.4194]; // Default to San Francisco

  // Adjust zoom level based on number of listings
  const zoom = mappableListings.length === 1 ? 13 : 10;

  useEffect(() => {
    // Fit bounds to show all markers when listings change
    if (mapRef.current && mappableListings.length > 1) {
      const bounds = L.latLngBounds(mappableListings.map((l) => [l.latitude, l.longitude]));
      mapRef.current.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [mappableListings]);

  if (mappableListings.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '500px',
          background: '#f5f5f5',
          borderRadius: '8px',
          color: '#666',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '18px', marginBottom: '8px' }}>📍 No listings with locations yet</p>
          <p style={{ fontSize: '14px' }}>
            Listings need latitude and longitude coordinates to appear on the map.
          </p>
        </div>
      </div>
    );
  }

  return (
    <MapContainer
      center={center}
      zoom={zoom}
      ref={mapRef}
      style={{ height: '600px', width: '100%', borderRadius: '8px' }}
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {mappableListings.map((listing) => (
        <Marker key={listing.id} position={[listing.latitude, listing.longitude]}>
          <Popup>
            <div style={{ minWidth: '200px' }}>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>{listing.title}</h3>
              {listing.location && (
                <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#666' }}>
                  📍 {listing.location}
                </p>
              )}
              {listing.description && (
                <p
                  style={{
                    margin: '8px 0',
                    fontSize: '14px',
                    maxHeight: '60px',
                    overflow: 'hidden',
                  }}
                >
                  {listing.description.substring(0, 100)}
                  {listing.description.length > 100 ? '...' : ''}
                </p>
              )}
              <button
                onClick={() => onListingClick && onListingClick(listing)}
                style={{
                  marginTop: '8px',
                  padding: '6px 12px',
                  background: '#007bff',
                  color: 'white',
                  border: 'none',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  width: '100%',
                }}
              >
                View Details
              </button>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
