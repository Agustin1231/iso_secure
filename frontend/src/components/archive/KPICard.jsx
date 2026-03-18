import React from 'react';

const KPICard = ({ title, value, unit, status, description }) => {
  return (
    <div className="glass-card kpi-card">
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <span className="kpi-label">{title}</span>
        <span className={`status-dot status-${status}`}></span>
      </div>
      <div className="kpi-value">
        {value} <span style={{ fontSize: '1rem', color: 'gray' }}>{unit}</span>
      </div>
      <p style={{ fontSize: '0.8rem', color: 'gray' }}>{description}</p>
    </div>
  );
};

export default KPICard;
