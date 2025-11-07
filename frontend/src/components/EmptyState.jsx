import React from 'react';

export default function EmptyState() {
  return (
    <div className="empty-state">
      <img src="/Design-Assets/Wireframe.png" alt="No listings" className="empty-illustration" />
      <h2>No listings yet</h2>
      <p>There are no active listings. Check back later or create a new opportunity.</p>
    </div>
  );
}
