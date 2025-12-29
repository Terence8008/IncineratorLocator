import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents, ImageOverlay } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from 'leaflet';
import { SiteService } from "./services/api";

// --- Leaflet Icon Fix ---
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const LAYER_BOUNDS = [[2.5929, 100.8087], [3.8654, 101.9704]];

function App() {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [data, setData] = useState({ prediction: null, features: null, insights: [] });
  const [activeLayer, setActiveLayer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showSidebar, setShowSidebar] = useState(true);

    const LANDUSE_COLORS = {
      1: "#a6d854", 
      2: "#8da0cb", 
      3: "#e78ac3", 
      4: "#ffd92f", 
      5: "#fc8d62", 
      6: "#66c2a5", 
      7: "#808080", 
      8: "#e41a1c", 
      9: "#7f0000", // Dark Red for KL
    };
    
  // Analysis Criteria Thresholds (Matches Backend)
  const thresholds = [
    { title: "Population Density", rules: [{ label: "Low (< 20)", level: "success" }, { label: "Moderate (20-80)", level: "warning" }, { label: "High (> 80)", level: "danger" }] },
    { title: "Water Proximity", rules: [{ label: "Safe (> 1000m)", level: "success" }, { label: "Caution (500-1000m)", level: "warning" }, { label: "Risk (< 500m)", level: "danger" }] },
    { title: "Road Logistics", rules: [{ label: "Connected (< 200m)", level: "success" }, { label: "Inaccessible (> 200m)", level: "danger" }] },
    {
      title: "Land Use Legend",
      rules: [
        { label: "1-3: Agriculture/Rural", color: LANDUSE_COLORS[3] },
        { label: "4-5: Residential/Commercial", color: LANDUSE_COLORS[5] },
        { label: "6: Industrial", color: LANDUSE_COLORS[6] },
        { label: "8: Urban Built-up", color: LANDUSE_COLORS[8] },
        { label: "9: City Center (KL/Putrajaya)", color: LANDUSE_COLORS[9] },
      ],
    },
  ];

  const handlePredict = async () => {
    if (!selectedPosition) return alert("Please select a location!");
    setLoading(true);
    try {
      const result = await SiteService.predict(selectedPosition[0], selectedPosition[1]);
      setData({ prediction: result.prediction, features: result.features, insights: result.insights || [] });
    } catch (err) {
      alert("Failed to get prediction from server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", overflow: "hidden", fontFamily: "sans-serif" }}>
      
      {/* 1. SIDEBAR: CRITERIA */}
      {showSidebar && (
        <div style={sidebarStyle}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "20px" }}>
            <h3 style={{ margin: 0 }}>Analysis Criteria</h3>
            <button onClick={() => setShowSidebar(false)} style={closeBtn}>×</button>
          </div>
          {thresholds.map((group, idx) => (
            <div key={idx} style={{ marginBottom: "15px" }}>
              <strong style={{ fontSize: "0.9em", color: "#444" }}>{group.title}</strong>
              {group.rules.map((rule, i) => (
                <div key={i} style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "0.75em", marginTop: "4px" }}>
                  <div style={{ 
                    width: 10, 
                    height: 10, 
                    borderRadius: "2px", 
                    background: rule.color || getLevelColor(rule.level),
                    border: "1px solid #ccc" 
                  }} />
                  {rule.label}
                </div>
              ))}
            </div>
          ))}
        </div>
      )}

      {/* Main Area  */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", position: "relative" }}>
        {!showSidebar && <button onClick={() => setShowSidebar(true)} style={openBtn}>☰ Criteria</button>}

        {/* MAP SECTION */}
        <div style={{ flex: 1, position: "relative" }}>
          <MapContainer center={[3.139, 101.686]} zoom={10} style={{ height: "100%" }}>
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            {activeLayer && <ImageOverlay key={activeLayer} url={SiteService.getLayerUrl(activeLayer)} bounds={LAYER_BOUNDS} opacity={0.6} />}
            {selectedPosition && <Marker position={selectedPosition} />}
            <LocationSelector onSelect={setSelectedPosition} />
          </MapContainer>
          <LayerControls active={activeLayer} onToggle={setActiveLayer} />
        </div>

        {/* RESULTS SECTION */}
        <div style={resultsPanel}>
          <div style={{ textAlign: "center" }}>
            <button onClick={handlePredict} disabled={loading} style={btnStyle}>{loading ? "Analyzing..." : "Analyze Site"}</button>
          </div>
          
          {data.prediction && (
            <div style={{ marginTop: "15px" }}>
              <h2 style={{ textAlign: "center", margin: "5px 0", color: data.prediction === "Suitable" ? "#28a745" : "#dc3545" }}>{data.prediction}</h2>
              
              <div style={featureSection}>
                <div style={featureGrid}>
                  {Object.entries(data.features).map(([k, v]) => (
                    <div key={k} style={featureItem}>
                      <span style={featureLabel}>{k.replace(/_/g, ' ')}:</span>
                      <span style={featureValue}>{typeof v === 'number' ? v.toFixed(2) : v}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div style={insightGrid}>
                {data.insights.map((ins, i) => (
                  <div key={i} style={{ ...insightCard, borderColor: getLevelColor(ins.level) }}>{ins.text}</div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// --- Helper Logic & Styles ---
const LocationSelector = ({ onSelect }) => { useMapEvents({ click(e) { onSelect([e.latlng.lat, e.latlng.lng]); } }); return null; };
const LayerControls = ({ active, onToggle }) => (
  <div style={floatingPanel}>
    <button style={active === 'population' ? activeBtn : {}} onClick={() => onToggle(active === 'population' ? null : 'population')}>Population</button>
    <button style={active === 'landuse' ? activeBtn : {}} onClick={() => onToggle(active === 'landuse' ? null : 'landuse')}>Land Use</button>
  </div>
);

const getLevelColor = (l) => l === 'danger' ? '#dc3545' : l === 'warning' ? '#ffc107' : '#28a745';
const sidebarStyle = { width: "260px", background: "#fff", borderRight: "1px solid #ddd", padding: "20px", zIndex: 1001, boxShadow: "2px 0 5px rgba(0,0,0,0.05)" };
const resultsPanel = { padding: "15px", background: "#fff", borderTop: "2px solid #eee", overflowY: "auto", maxHeight: "45%" };
const floatingPanel = { position: "absolute", top: 10, right: 10, zIndex: 1000, background: "white", padding: 10, borderRadius: 8, display: "flex", flexDirection: "column", gap: 5, boxShadow: "0 2px 8px rgba(0,0,0,0.15)" };
const featureSection = { background: "#f8f9fa", padding: "10px", borderRadius: "8px", marginBottom: "10px" };
const featureGrid = { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: "8px" };
const featureItem = { display: "flex", justifyContent: "space-between", padding: "4px 8px", background: "#fff", border: "1px solid #eee", borderRadius: "4px" };
const featureLabel = { fontSize: "0.75em", color: "#777", textTransform: "capitalize" };
const featureValue = { fontSize: "0.85em", fontWeight: "bold" };
const insightGrid = { display: "flex", flexWrap: "wrap", gap: "8px", justifyContent: "center" };
const insightCard = { padding: "10px", background: "#fff", borderLeft: "4px solid", fontSize: "0.8em", width: "180px", boxShadow: "0 1px 3px rgba(0,0,0,0.05)" };
const btnStyle = { padding: "10px 30px", background: "#007bff", color: "#fff", border: "none", borderRadius: "5px", cursor: "pointer", fontWeight: "bold" };
const activeBtn = { background: "#007bff", color: "#fff" };
const closeBtn = { background: "none", border: "none", fontSize: "20px", cursor: "pointer" };
const openBtn = { position: "absolute", top: 10, left: 10, zIndex: 1000, background: "#fff", border: "1px solid #ccc", padding: "5px 10px", borderRadius: "4px", cursor: "pointer" };

export default App;