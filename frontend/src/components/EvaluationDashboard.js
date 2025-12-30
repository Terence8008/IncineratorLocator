import React from 'react';

const EvaluationDashboard = () => {
  const API_BASE = "http://localhost:8000/static"; 

  return (
    <div style={{ padding: '30px', backgroundColor: '#f9f9f9', height: '100%', overflowY: 'auto' }}>
      <h1 style={{ marginBottom: '10px' }}>Model Performance Analytics</h1>
      <p style={{ color: '#666', marginBottom: '30px' }}>Detailed metrics of the Random Forest Classifier trained on Selangor data.</p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '20px' }}>
        <div style={cardStyle}>
          <h3>Confusion Matrix</h3>
          <img src={`${API_BASE}/confusion_matrix.png`} alt="Confusion Matrix" style={{ width: '100%', borderRadius: '5px' }} />
          <p style={descStyle}>Evaluates how many "Suitable" sites were correctly identified vs false alarms.</p>
        </div>

        <div style={cardStyle}>
          <h3>ROC Curve</h3>
          <img src={`${API_BASE}/roc_curve.png`} alt="ROC Curve" style={{ width: '100%', borderRadius: '5px' }} />
          <p style={descStyle}>A measure of the model's ability to distinguish between classes (AUC should be close to 1.0).</p>
        </div>

        <div style={cardStyle}>
          <h3>Feature Importance</h3>
          <img src={`${API_BASE}/feature_importance.png`} alt="Feature Importance" style={{ width: '100%', borderRadius: '5px' }} />
          <p style={descStyle}>Ranking of which environmental factors influenced the model the most during training.</p>
        </div>
      </div>
    </div>
  );
};

const cardStyle = { background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 10px rgba(0,0,0,0.1)' };
const descStyle = { fontSize: '0.85rem', color: '#7f8c8d', marginTop: '10px', fontStyle: 'italic' };

export default EvaluationDashboard;