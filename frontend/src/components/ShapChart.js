import React from 'react';

const ShapChart = ({ shapValues }) => {
  if (!shapValues) return null;

  // Features we want to display
  const features = Object.entries(shapValues);

  return (
    <div style={{ marginTop: '15px', borderTop: '1px solid #eee', paddingTop: '10px' }}>
      <h4 style={{ fontSize: '0.9rem', marginBottom: '8px' }}>AI Decision Impact (SHAP)</h4>
      <p style={{ fontSize: '0.7rem', color: '#666' }}>Influence on "Suitable" prediction:</p>
      
      {features.map(([name, value]) => (
        <div key={name} style={{ margin: '10px 0' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem' }}>
            <span style={{ textTransform: 'capitalize' }}>{name.replace(/_/g, ' ')}</span>
            <span style={{ color: value >= 0 ? '#27ae60' : '#c0392b', fontWeight: 'bold' }}>
              {value >= 0 ? '+' : ''}{value.toFixed(3)}
            </span>
          </div>
          <div style={styles.barContainer}>
            <div style={{
              ...styles.bar,
              width: `${Math.min(Math.abs(value) * 100, 100)}%`,
              backgroundColor: value >= 0 ? '#2ecc71' : '#e74c3c',
              marginLeft: value >= 0 ? '0' : 'auto' // Simple way to show direction
            }} />
          </div>
        </div>
      ))}
    </div>
  );
};

const styles = {
  barContainer: { height: '8px', background: '#ecf0f1', borderRadius: '4px', marginTop: '4px', display: 'flex' },
  bar: { height: '100%', borderRadius: '4px', transition: 'width 0.5s ease' }
};

export default ShapChart;