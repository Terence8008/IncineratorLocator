import React from 'react';

const ScenarioSliders = ({ weights, setWeights }) => {
  const updateWeight = (key, val) => {
    setWeights(prev => ({ ...prev, [key]: parseFloat(val) }));
  };

  const labels = {
    w_pop: "Population Importance",
    w_river: "Environmental Safety (River)",
    w_road: "Logistics Priority (Roads)",
    w_land: "Land Use Match"
  };

  return (
    <div style={containerStyle}>
      <h4 style={{ marginBottom: '10px', fontSize: '0.9rem' }}>Simulation Weights</h4>
      {Object.entries(weights).map(([key, value]) => (
        <div key={key} style={{ marginBottom: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
            <span>{labels[key]}</span>
            <span style={{ fontWeight: 'bold' }}>{(value * 100).toFixed(0)}%</span>
          </div>
          <input 
            type="range" min="0" max="1" step="0.05"
            value={value}
            onChange={(e) => updateWeight(key, e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>
      ))}
      <p style={{ fontSize: '0.65rem', fontStyle: 'italic', color: '#666' }}>
        *Adjust weights to see how policy affects the site score.
      </p>
    </div>
  );
};

const containerStyle = {
  padding: '15px',
  background: '#f8f9fa',
  borderRadius: '8px',
  border: '1px solid #dee2e6',
  marginTop: '15px'
};

export default ScenarioSliders;