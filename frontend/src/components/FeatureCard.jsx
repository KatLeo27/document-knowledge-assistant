import React from 'react';

export default function FeatureCard({ icon: Icon, color, title, description }) {
  return (
    <div className="feature-card">
      <div className={`feature-icon-wrap ${color}`}>
        <Icon size={20} />
      </div>
      <div>
        <h3 className="feature-title">{title}</h3>
        <p className="feature-desc">{description}</p>
      </div>
    </div>
  );
}
