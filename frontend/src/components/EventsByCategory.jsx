import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function EventsByCategory() {
  const [eventsByCategory, setEventsByCategory] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', name: 'All Events', icon: '🎉' },
    { id: 'community', name: 'Community', icon: '🤝', source: 'community' },
    { id: 'music', name: 'Music & Concerts', icon: '🎵', tmCategory: 'music', sgType: 'concert' },
    { id: 'sports', name: 'Sports', icon: '⚽', tmCategory: 'sports', sgType: 'sports' },
    { id: 'theater', name: 'Theater & Arts', icon: '🎭', tmCategory: 'arts', sgType: 'theater' },
    { id: 'family', name: 'Family', icon: '👨‍👩‍👧‍👦', tmCategory: 'family', sgType: 'family' },
  ];

  useEffect(() => {
    async function fetchEventsByCategory() {
      setLoading(true);
      setError(null);
      const results = {};

      try {
        if (selectedCategory === 'all') {
          // Fetch all events
          const res = await fetch(`${API_URL}/api/events/all?city=Houston&state=TX`);
          if (!res.ok) throw new Error(`status ${res.status}`);
          const data = await res.json();
          results.all = data.events || [];
        } else {
          // Fetch specific category
          const category = categories.find(c => c.id === selectedCategory);

          if (category && category.source === 'community') {
            // Fetch community events from PredictHQ
            const res = await fetch(
              `${API_URL}/api/events/community?city=Houston&state=TX`
            );
            if (res.ok) {
              const data = await res.json();
              results[selectedCategory] = data.events || [];
            }
          } else if (category && category.tmCategory) {
            // Fetch from Ticketmaster for other categories
            const res = await fetch(
              `${API_URL}/api/events/ticketmaster?city=Houston&state=TX&category=${category.tmCategory}`
            );
            if (res.ok) {
              const data = await res.json();
              results[selectedCategory] = data.events || [];
            }
          }
        }

        setEventsByCategory(results);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchEventsByCategory();
  }, [selectedCategory]);

  if (loading) return <p style={{ textAlign: 'center', padding: 20 }}>Loading events...</p>;
  if (error) return <p className="error" style={{ textAlign: 'center', padding: 20 }}>Error: {error}</p>;

  const events = eventsByCategory[selectedCategory] || [];

  return (
    <section style={{ marginTop: 32, maxWidth: 1200, margin: '32px auto', padding: '0 20px' }}>
      <h2 style={{ marginBottom: 20 }}>🎉 Houston Public Events</h2>

      {/* Category Tabs */}
      <div style={{
        display: 'flex',
        gap: 10,
        marginBottom: 24,
        overflowX: 'auto',
        padding: '10px 0'
      }}>
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            style={{
              padding: '10px 20px',
              border: 'none',
              borderRadius: 20,
              background: selectedCategory === cat.id ? '#007bff' : '#f0f0f0',
              color: selectedCategory === cat.id ? 'white' : '#333',
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              fontSize: 14,
              fontWeight: selectedCategory === cat.id ? 'bold' : 'normal',
              transition: 'all 0.3s ease'
            }}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      {/* Events List */}
      {events.length === 0 ? (
        <p style={{ textAlign: 'center', padding: 40, color: '#666' }}>
          No events found in this category.
        </p>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: 20
        }}>
          {events.map((event) => (
            <div
              key={event.id}
              style={{
                border: '1px solid #e0e0e0',
                borderRadius: 12,
                padding: 16,
                background: 'white',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
              }}
            >
              {(event.image || event.logo) && (
                <img
                  src={event.image || event.logo}
                  alt={event.name}
                  style={{
                    width: '100%',
                    height: 180,
                    objectFit: 'cover',
                    borderRadius: 8,
                    marginBottom: 12
                  }}
                />
              )}

              <h3 style={{
                fontSize: 16,
                fontWeight: 'bold',
                marginBottom: 8,
                color: '#333'
              }}>
                <a
                  href={event.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: '#007bff', textDecoration: 'none' }}
                >
                  {event.name}
                </a>
              </h3>

              <div style={{ fontSize: 14, color: '#666', marginBottom: 4 }}>
                📅 {event.start ? new Date(event.start).toLocaleDateString() : 'TBA'}
                {event.start_time && ` at ${event.start_time}`}
              </div>

              {event.venue && (
                <div style={{ fontSize: 14, color: '#666', marginBottom: 8 }}>
                  📍 {event.venue}
                </div>
              )}

              {event.source && (
                <span style={{
                  display: 'inline-block',
                  padding: '4px 8px',
                  background: event.source === 'ticketmaster' ? '#026cdf' : '#7b68ee',
                  color: 'white',
                  borderRadius: 12,
                  fontSize: 11,
                  fontWeight: 'bold',
                  textTransform: 'uppercase'
                }}>
                  {event.source}
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
