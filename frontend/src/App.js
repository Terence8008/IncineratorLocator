import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents, ImageOverlay } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from 'leaflet';
import "./App.css";
import { SiteService } from "./services/api";
import EvaluationDashboard from "./components/EvaluationDashboard"; 
import ShapChart from "./components/ShapChart";
import ScenarioSliders from "./components/ScenarioSliders";
import RouteInfoPanel from "./components/RouteInfoPanel"

// --- Leaflet Icon Fix ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const LAYER_BOUNDS = [[2.5929, 100.8087], [3.8654, 101.9704]];

// --- Sub-Components moved inside or defined properly ---
const LocationSelector = ({ onSelect }) => {
  useMapEvents({
    click(e) {
      onSelect([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
};

const LayerControls = ({ active, onToggle }) => (
  <div className="layer-controls">
    <button className={`layer-btn ${active === 'population' ? 'active' : ''}`} onClick={() => onToggle(active === 'population' ? null : 'population')}>Population Heatmap</button>
    <button className={`layer-btn ${active === 'landuse' ? 'active' : ''}`} onClick={() => onToggle(active === 'landuse' ? null : 'landuse')}>Land Use Map</button>
  </div>
);

function App() {
  const [activeView, setActiveView] = useState("map");
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingRoute, setLoadingRoute] = useState(false); 
  const [showSidebar, setShowSidebar] = useState(true);
  const [activeLayer, setActiveLayer] = useState(null);
  const [weights, setWeights] = useState({ w_pop: 0.25, w_river: 0.25, w_road: 0.25, w_land: 0.25 });
  const [data, setData] = useState({ prediction: null, policy_score: 0, features: null, insights: [], shap_explanation: null });
  const [routeData, setRouteData] = useState(null);
  
  const featureMeta = {
    population: { label: "Population Density", unit: "people/km²" },
    land_use: { label: "Land Use Category", unit: "Class ID" },
    dist_river_m: { label: "Distance to River", unit: "meters" },
    dist_road_m: { label: "Distance to Road", unit: "meters" }
  };
  
  const LANDUSE_COLORS = {
    1: "#a6d854", 2: "#8da0cb", 3: "#e78ac3", 4: "#ffd92f", 
    5: "#fc8d62", 6: "#66c2a5", 7: "#808080", 8: "#e41a1c", 9: "#7f0000",
  };
    
  const thresholds = [
    { title: "Population Density", rules: [{ label: "Low (< 20)", level: "success" }, { label: "Moderate (20-80)", level: "warning" }, { label: "High (> 80)", level: "danger" }] },
    { title: "Water Proximity", rules: [{ label: "Safe (> 1000m)", level: "success" }, { label: "Caution (500-1000m)", level: "warning" }, { label: "Risk (< 500m)", level: "danger" }] },
    { title: "Road Logistics", rules: [{ label: "Connected (< 200m)", level: "success" }, { label: "Inaccessible (> 200m)", level: "danger" }] },
    {
      title: "Land Use Legend",
      rules: [
        { label: "1: Non Paddy Agriculture", color: LANDUSE_COLORS[1] },
        { label: "2-3: Agriculture/Rural", color: LANDUSE_COLORS[3] },
        { label: "4-5: Residential/Commercial", color: LANDUSE_COLORS[5] },
        { label: "6: Industrial", color: LANDUSE_COLORS[6] },
        { label: "7: Road (No Color)" },
        { label: "8: Urban Built-up", color: LANDUSE_COLORS[8] },
        { label: "9: City Center (KL/Putrajaya)", color: LANDUSE_COLORS[9] },
      ],
    },
  ];

  const getLevelColor = (l) => l === 'danger' ? '#dc3545' : l === 'warning' ? '#ffc107' : '#28a745';

  const handlePredict = async () => {
    if (!selectedPosition) return alert("Please select a location!");
    setLoading(true);
    setRouteData(null);

    // Check console to see if weights has values like {w_pop: 0.25, ...}
    console.log("Weights in App.js state:", weights); 

    try {
      const result = await SiteService.predict(
        selectedPosition[0], 
        selectedPosition[1], 
        weights 
      );
      
      setData({ 
        prediction: result.prediction, 
        policy_score: result.policy_score, 
        features: result.features, 
        insights: result.insights || [],
        shap_explanation: result.shap_explanation 
      });
    } catch (err) {
      console.error("Predict Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckRoute = async () => {
    if (!selectedPosition) {
      alert("Please select a location first!");
      return;
    }

    setLoadingRoute(true);

    try {
      const result = await SiteService.checkRoute(
        selectedPosition[0],
        selectedPosition[1]
      );
      
      setRouteData(result);
      console.log("Route optimized:", result);
    } catch (err) {
      console.error("Route optimization error:", err);
      alert(`Failed to optimize route: ${err.message}`);
    } finally {
      setLoadingRoute(false);
    }
  };


  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column", overflow: "hidden", fontFamily: "sans-serif" }}>
      
      {/* NAVIGATION BAR */}
      <div className="nav-bar">
        <div className="logo">Selangor AI Site Analysis</div>
        <div className="nav-buttons">
          <button className={`tab-btn ${activeView === "map" ? "active" : ""}`} onClick={() => setActiveView("map")}>Map Explorer</button>
          <button className={`tab-btn ${activeView === "evaluation" ? "active" : ""}`} onClick={() => setActiveView("evaluation")}>Model Analytics</button>
        </div>
      </div>

      {activeView === "map" ? (
        <div className="main-content">
          {/* 1. SIDEBAR: CRITERIA */}
          {showSidebar && (
            <div className="sidebar">
              <div className="sidebar-header">
                <h3>Analysis Criteria</h3>
                <button onClick={() => setShowSidebar(false)} className="close-btn">×</button>
              </div>
              <ScenarioSliders weights={weights} setWeights={setWeights} />
              {thresholds.map((group, idx) => (
                <div key={idx} style={{ marginBottom: "15px" }}>
                  <strong style={{ fontSize: "0.9em", color: "#444" }}>{group.title}</strong>
                  {group.rules.map((rule, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.75em", marginTop: "4px" }}>
                      <div style={{ width: 10, height: 10, borderRadius: "2px", background: rule.color || getLevelColor(rule.level), border: "1px solid #ccc" }} />
                      {rule.label}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}

          {/* Main Area */}
          <div className="map-wrapper">
            {!showSidebar && <button onClick={() => setShowSidebar(true)} className="open-sidebar-btn">☰ Criteria</button>}

            {/* MAP SECTION */}
            <div style={{ flex: 1, position: "relative" }}>
              <MapContainer center={[3.139, 101.686]} zoom={10} style={{ height: "100%" }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                {activeLayer && <ImageOverlay key={activeLayer} url={SiteService.getLayerUrl(activeLayer)} bounds={LAYER_BOUNDS} opacity={0.6} />}
                {selectedPosition && <Marker position={selectedPosition} />}

                {routeData && routeData.optimized_route && (
                  <Polyline
                    positions={routeData.optimized_route.path_coordinates.map(
                      coord => [coord[1], coord[0]] // Convert [lon, lat] to [lat, lon]
                    )}
                    color="#ff6f00"
                    weight={4}
                    opacity={0.8}
                  />
                )}


                {routeData && routeData.nearest_landfill && (
                  <Marker 
                    position={[
                      routeData.nearest_landfill.coordinates[1],
                      routeData.nearest_landfill.coordinates[0]
                    ]}
                    icon={new L.Icon({
                      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png',
                      iconSize: [25, 41],
                      iconAnchor: [12, 41],
                    })}
                  />
                )}

                <LocationSelector onSelect={setSelectedPosition} />
              </MapContainer>
              <LayerControls active={activeLayer} onToggle={setActiveLayer} />
            </div>

            {/* RESULTS SECTION */}
            <div className="results-panel">
              <div style={{ textAlign: "center" }}>
                <button onClick={handlePredict} disabled={loading} className="analyze-btn">
                  Analyzing Site
                </button>

                {data.prediction === "Suitable" && (
                  <button 
                    onClick={handleCheckRoute} 
                    disabled={loadingRoute}
                    className="route-btn"
                    style={{ 
                      marginLeft: '10px',
                      backgroundColor: '#2e7d32',
                      color: 'white',
                      padding: '12px 24px',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: loadingRoute ? 'not-allowed' : 'pointer',
                      fontSize: '16px',
                      fontWeight: 'bold',
                      opacity: loadingRoute ? 0.6 : 1
                    }}
                  >
                    {loadingRoute ? "🔄 Optimizing..." : "2️⃣ Check Route to Landfill"}
                  </button>
                )}
              </div>

              
              {data.prediction && (
                <div className="outcome-grid">
                  
                  {/* Column 1: AI & Policy Score */}
                  <div className="assessment-col">
                    <h3 style={{ fontSize: '1.3rem', marginBottom: '10px' }}>Site Suitability</h3>
                    <div className="policy-gauge">
                          <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: '5px' }}>Policy Alignment</div>
                          
                          {/* Use logic to show 0 if data is missing */}
                          <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: '#3498db' }}>
                              {data.policy_score !== undefined ? Math.round(data.policy_score) : 0}%
                          </div>

                          <div className="gauge-bar-base">
                              <div 
                                  className="gauge-bar-fill" 
                                  style={{ 
                                      // Ensure width is at least 0%
                                      width: `${data.policy_score || 0}%`, 
                                      backgroundColor: data.policy_score > 50 ? "#3498db" : "#e74c3c" 
                                  }} 
                              />
                          </div>
                      </div>
                    <h2 style={{ color: data.prediction === "Suitable" ? "#28a745" : "#dc3545", textAlign: 'center', marginTop: '20px' }}>
                      Result: {data.prediction}
                    </h2>
                  </div>

                  {/* Column 2: Site Features */}
                  <div className="features-col">
                    <h3 style={{ fontSize: '1.3rem', marginBottom: '15px' }}>Extracted Features</h3>
                    <div className="feature-list">
                      {data.features && Object.entries(data.features).map(([k, v]) => (
                        <div key={k} className="feature-card">
                          <span className="feature-label-text">
                            {featureMeta[k]?.label || k.replace(/_/g, ' ')}
                          </span>
                          <strong className="feature-value-text">
                            {typeof v === 'number' ? v.toFixed(1) : v} 
                            <span className="feature-unit"> {featureMeta[k]?.unit || ''}</span>
                          </strong>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Column 3: XAI (SHAP) & Insights */}
                  <div className="shap-col">
                    <div className="shap-section">
                      <h3 style={{ fontSize: '1.3rem', marginBottom: '10px' }}>AI Decision Impact (SHAP)</h3>
                      <ShapChart shapValues={data.shap_explanation} />
                    </div>
                  </div>
                    
                  <div className="shap-col">  
                    <div className="insight-section">
                      <h3 style={{ fontSize: '1.3rem', marginBottom: '10px' }}>Strategic Insights</h3>
                      <div className="insight-list">
                        {data.insights.map((ins, i) => (
                          <div key={i} className="insight-card" style={{ borderLeftColor: getLevelColor(ins.level) }}>
                            {ins.text}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {routeData && (
                    <div className="route-col" style={{ gridColumn: '1 / -1' }}>
                      <RouteInfoPanel routeData={routeData} />
                    </div>
                  )}

                </div>
              )}

            </div>
          </div>
        </div>
      ) : (
        <EvaluationDashboard />
      )}
    </div>
  );
}


export default App;