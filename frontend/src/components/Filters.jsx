import React from 'react';

const chips = ['All', 'Community', 'Environment', 'Education', 'Health', 'Animals'];

export default function Filters({ active, onChange }) {
  return (
    <div className="filters">
      <div className="chips">
        {chips.map((c) => (
          <button
            key={c}
            className={`chip ${active === c ? 'active' : ''}`}
            onClick={() => onChange && onChange(c)}
          >
            {c}
          </button>
        ))}
      </div>
    </div>
  );
}
