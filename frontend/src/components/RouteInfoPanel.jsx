import React from 'react';

const RouteInfoPanel = ({ routeData }) => {
  if (!routeData) return null;

  const { nearest_landfill, optimized_route } = routeData;

  return (
    <div className="route-info-panel">
      <h3 style={{ fontSize: '1.2rem', marginBottom: '12px', color: '#e65100' }}>
        🚚 Optimized Route to Nearest Landfill
      </h3>
      
      <div className="route-info-grid">
        <div className="route-info-item">
          <span className="route-label">Target Landfill:</span>
          <span className="route-value">{nearest_landfill.name}</span>
        </div>

        <div className="route-info-item">
          <span className="route-label">Road Distance:</span>
          <span className="route-value">{optimized_route.road_distance_km} km</span>
        </div>

        <div className="route-info-item">
          <span className="route-label">Straight Distance:</span>
          <span className="route-value">{nearest_landfill.straight_line_distance_km} km</span>
        </div>

        <div className="route-info-item">
          <span className="route-label">Distance Ratio:</span>
          <span className="route-value">{optimized_route.distance_ratio}x</span>
        </div>

        <div className="route-info-item">
          <span className="route-label">Route Waypoints:</span>
          <span className="route-value">{optimized_route.num_waypoints}</span>
        </div>

        <div className="route-info-item">
          <span className="route-label">Landfill Location:</span>
          <span className="route-value" style={{ fontSize: '0.8em' }}>
            [{nearest_landfill.coordinates[1].toFixed(4)}, {nearest_landfill.coordinates[0].toFixed(4)}]
          </span>
        </div>
      </div>
    </div>
  );
};

export default RouteInfoPanel;