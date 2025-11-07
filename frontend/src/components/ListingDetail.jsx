import React, { useState, useEffect } from 'react';
import EditListingForm from './EditListingForm';
import ReviewForm from './ReviewForm';

export default function ListingDetail({
  listing,
  onClose,
  token,
  user,
  onListingUpdated,
  onListingDeleted,
}) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [reviews, setReviews] = useState([]);
  const [averageRating, setAverageRating] = useState(null);
  const [loadingReviews, setLoadingReviews] = useState(false);

  if (!listing) return null;

  const isOwner = user && listing.owner_id === user.id;

  // Fetch reviews and average rating on mount
  useEffect(() => {
    async function fetchReviews() {
      setLoadingReviews(true);
      try {
        const [reviewsRes, ratingRes] = await Promise.all([
          fetch(`http://127.0.0.1:5000/listings/${listing.id}/reviews`),
          fetch(`http://127.0.0.1:5000/listings/${listing.id}/average-rating`),
        ]);

        if (reviewsRes.ok) {
          const reviewsData = await reviewsRes.json();
          setReviews(reviewsData.reviews || []);
        }

        if (ratingRes.ok) {
          const ratingData = await ratingRes.json();
          setAverageRating(ratingData.average_rating);
        }
      } catch (err) {
        console.error('Error fetching reviews:', err);
      } finally {
        setLoadingReviews(false);
      }
    }

    fetchReviews();
  }, [listing.id]);

  function handleReviewAdded(newReview) {
    setReviews([newReview, ...reviews]);
    // Recalculate average
    if (reviews.length === 0) {
      setAverageRating(newReview.rating);
    } else {
      const total = reviews.reduce((sum, r) => sum + r.rating, newReview.rating);
      setAverageRating(total / (reviews.length + 1));
    }
  }

  async function handleSignUp() {
    if (!token) {
      alert('Please log in to sign up for this listing');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`http://127.0.0.1:5000/listings/${listing.id}/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || `Failed with status ${res.status}`);
      }

      setSuccess(true);
      setTimeout(() => {
        setShowConfirm(false);
        setSuccess(false);
        setMessage('');
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!token) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`http://127.0.0.1:5000/listings/${listing.id}`, {
        method: 'DELETE',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to delete listing');
      }

      if (onListingDeleted) onListingDeleted(listing.id);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="detail-overlay" role="dialog" aria-modal="true">
        <div className="detail-card">
          <header className="detail-header">
            <h2>{listing.title}</h2>
            <button className="close" onClick={onClose} aria-label="Close">
              ×
            </button>
          </header>
          <div className="detail-body">
            {listing.location && (
              <p>
                <strong>Location:</strong> {listing.location}
              </p>
            )}
            {listing.description && <p>{listing.description}</p>}
            <p>
              <small>Created: {new Date(listing.created_at || Date.now()).toLocaleString()}</small>
            </p>

            {/* Reviews Section */}
            <div style={{ marginTop: '24px', borderTop: '1px solid #eee', paddingTop: '16px' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '16px',
                }}
              >
                <h3 style={{ margin: 0 }}>Reviews</h3>
                {averageRating !== null && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '20px', color: '#ffc107' }}>★</span>
                    <span style={{ fontWeight: 'bold' }}>{averageRating.toFixed(1)}</span>
                    <span style={{ color: '#666', fontSize: '14px' }}>({reviews.length})</span>
                  </div>
                )}
              </div>

              {!isOwner && user && (
                <button
                  onClick={() => setShowReviewForm(true)}
                  style={{
                    width: '100%',
                    padding: '8px',
                    marginBottom: '16px',
                    background: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  Write a Review
                </button>
              )}

              {loadingReviews ? (
                <p style={{ textAlign: 'center', color: '#666' }}>Loading reviews...</p>
              ) : reviews.length === 0 ? (
                <p style={{ textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
                  No reviews yet. Be the first to review!
                </p>
              ) : (
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                  {reviews.map((review) => (
                    <div
                      key={review.id}
                      style={{
                        padding: '12px',
                        marginBottom: '12px',
                        background: '#f9f9f9',
                        borderRadius: '4px',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          marginBottom: '8px',
                        }}
                      >
                        <div>
                          <strong>{review.user_email}</strong>
                          <div style={{ color: '#ffc107', fontSize: '16px' }}>
                            {'★'.repeat(review.rating)}
                            {'☆'.repeat(5 - review.rating)}
                          </div>
                        </div>
                        <small style={{ color: '#666' }}>
                          {new Date(review.created_at).toLocaleDateString()}
                        </small>
                      </div>
                      {review.comment && <p style={{ margin: 0 }}>{review.comment}</p>}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {error && (
              <div className="error" role="alert">
                {error}
              </div>
            )}

            {success && (
              <div className="success" role="alert">
                ✓ Successfully signed up! Owner will be notified.
              </div>
            )}
          </div>

          {!showConfirm && !showDeleteConfirm ? (
            <footer className="detail-footer">
              {isOwner ? (
                <div style={{ display: 'flex', gap: '8px', width: '100%' }}>
                  <button className="cta" onClick={() => setShowEdit(true)} style={{ flex: 1 }}>
                    Edit
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(true)}
                    style={{
                      flex: 1,
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      padding: '8px 16px',
                      borderRadius: '4px',
                      cursor: 'pointer',
                    }}
                  >
                    Delete
                  </button>
                </div>
              ) : (
                <button
                  className="cta"
                  onClick={() => setShowConfirm(true)}
                  disabled={loading || success}
                >
                  {success ? '✓ Signed Up' : 'Sign Up'}
                </button>
              )}
            </footer>
          ) : showDeleteConfirm ? (
            <div className="confirm-delete" style={{ padding: '16px' }}>
              <h3>Confirm Deletion</h3>
              <p>
                Are you sure you want to delete <strong>{listing.title}</strong>? This action cannot
                be undone.
              </p>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button onClick={() => setShowDeleteConfirm(false)} disabled={loading}>
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={loading}
                  style={{
                    background: '#dc3545',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '4px',
                    cursor: 'pointer',
                  }}
                >
                  {loading ? 'Deleting...' : 'Yes, Delete'}
                </button>
              </div>
            </div>
          ) : (
            <div className="confirm-signup">
              <h3>Confirm Sign-Up</h3>
              <p>
                Would you like to sign up for: <strong>{listing.title}</strong>?
              </p>
              <textarea
                placeholder="Optional: Add a message for the listing owner..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                rows={3}
                style={{ width: '100%', marginBottom: '12px', padding: '8px' }}
              />
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => {
                    setShowConfirm(false);
                    setMessage('');
                    setError(null);
                  }}
                  disabled={loading}
                >
                  Cancel
                </button>
                <button className="cta" onClick={handleSignUp} disabled={loading}>
                  {loading ? 'Signing up...' : 'Confirm Sign-Up'}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {showEdit && (
        <EditListingForm
          listing={listing}
          token={token}
          onClose={() => setShowEdit(false)}
          onUpdated={onListingUpdated}
        />
      )}

      {showReviewForm && (
        <ReviewForm
          listing={listing}
          token={token}
          onClose={() => setShowReviewForm(false)}
          onReviewAdded={handleReviewAdded}
        />
      )}
    </>
  );
}
