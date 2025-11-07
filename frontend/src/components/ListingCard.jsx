import React, { useState, useEffect } from 'react';

export default function ListingCard({ listing = {}, onOpen }) {
  const { title, description, image_url, location, id, category } = listing;
  const [averageRating, setAverageRating] = useState(null);
  const [reviewCount, setReviewCount] = useState(0);

  useEffect(() => {
    if (!id) return;

    async function fetchRating() {
      try {
        const [ratingRes, reviewsRes] = await Promise.all([
          fetch(`http://127.0.0.1:5000/listings/${id}/average-rating`),
          fetch(`http://127.0.0.1:5000/listings/${id}/reviews`),
        ]);

        if (ratingRes.ok) {
          const ratingData = await ratingRes.json();
          setAverageRating(ratingData.average_rating);
        }

        if (reviewsRes.ok) {
          const reviewsData = await reviewsRes.json();
          setReviewCount(reviewsData.reviews?.length || 0);
        }
      } catch (err) {
        console.error('Error fetching rating:', err);
      }
    }

    fetchRating();
  }, [id]);

  // Category styling
  const getCategoryColor = (cat) => {
    const colors = {
      'Community': '#8b5cf6',
      'Environment': '#10b981',
      'Education': '#3b82f6',
      'Health': '#ef4444',
      'Animals': '#f59e0b',
    };
    return colors[cat] || '#6b7280';
  };

  return (
    <li className="listing-item">
      <article className="card" role="article" aria-label={title || 'Listing'}>
        <div className="card-media" aria-hidden={image_url ? 'false' : 'true'}>
          {image_url ? (
            <img src={image_url} alt={title || 'Listing image'} loading="lazy" />
          ) : (
            <div className="placeholder" aria-hidden="true">
              📷
            </div>
          )}
          {category && (
            <div 
              className="category-badge"
              style={{
                backgroundColor: getCategoryColor(category),
              }}
            >
              {category}
            </div>
          )}
        </div>

        <div className="card-content">
          <h3 className="card-title">{title || 'Untitled listing'}</h3>

          {averageRating !== null && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px' }}>
              <span style={{ color: '#ffc107', fontSize: '16px' }}>★</span>
              <span style={{ fontWeight: 'bold', fontSize: '14px' }}>{averageRating.toFixed(1)}</span>
              <span style={{ color: '#666', fontSize: '12px' }}>({reviewCount})</span>
            </div>
          )}

          <p className="card-desc">{description || 'No description provided.'}</p>

          {location && (
            <div className="location-tag">
              <span>📍</span> {location}
            </div>
          )}
        </div>

        <div className="card-footer">
          <button className="btn btn-primary" onClick={() => onOpen && onOpen(listing)}>
            View Details
          </button>
        </div>
      </article>
    </li>
  );
}
