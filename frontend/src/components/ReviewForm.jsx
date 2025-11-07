import React, { useState } from 'react';

export default function ReviewForm({ listing, token, onClose, onReviewAdded }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hoveredRating, setHoveredRating] = useState(0);

  async function handleSubmit(e) {
    e.preventDefault();

    if (!token) {
      setError('Please log in to submit a review');
      return;
    }

    if (rating < 1 || rating > 5) {
      setError('Rating must be between 1 and 5 stars');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`http://127.0.0.1:5000/listings/${listing.id}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ rating, comment }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to submit review');
      }

      const newReview = await res.json();
      if (onReviewAdded) onReviewAdded(newReview);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="detail-overlay" role="dialog" aria-modal="true">
      <div className="detail-card" style={{ maxWidth: '500px' }}>
        <header className="detail-header">
          <h2>Review: {listing.title}</h2>
          <button className="close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit}>
          <div className="detail-body">
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                Rating
              </label>
              <div style={{ display: 'flex', gap: '4px', fontSize: '32px' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoveredRating(star)}
                    onMouseLeave={() => setHoveredRating(0)}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: 0,
                      color: star <= (hoveredRating || rating) ? '#ffc107' : '#e0e0e0',
                      transition: 'color 0.2s',
                    }}
                    aria-label={`${star} star${star !== 1 ? 's' : ''}`}
                  >
                    ★
                  </button>
                ))}
              </div>
              <p style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
                {rating} star{rating !== 1 ? 's' : ''}
              </p>
            </div>

            <div>
              <label
                htmlFor="comment"
                style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}
              >
                Comment (optional)
              </label>
              <textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Share your experience with this listing..."
                rows={5}
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontFamily: 'inherit',
                  fontSize: '14px',
                }}
                maxLength={500}
              />
              <p style={{ textAlign: 'right', color: '#666', fontSize: '12px', marginTop: '4px' }}>
                {comment.length}/500
              </p>
            </div>

            {error && (
              <div className="error" role="alert" style={{ marginTop: '16px' }}>
                {error}
              </div>
            )}
          </div>

          <footer className="detail-footer">
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button type="button" onClick={onClose} disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="cta" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          </footer>
        </form>
      </div>
    </div>
  );
}
