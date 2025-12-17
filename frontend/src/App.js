import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents, ImageOverlay } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from 'leaflet';

// Import our new service
import { SiteService } from "./services/api";

// --- Leaflet Icon Fix (Standard) ---
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

  // Use the service to handle the click
  const handlePredict = async () => {
    if (!selectedPosition) return alert("Please select a location!");
    
    setLoading(true);
    try {
      const result = await SiteService.predict(selectedPosition[0], selectedPosition[1]);
      setData({
        prediction: result.prediction,
        features: result.features,
        insights: result.insights || []
      });
    } catch (err) {
      alert("Failed to get prediction from server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ width: "100vw", height: "100vh", display: "flex", flexDirection: "column" }}>
      {/* 1. MAP SECTION */}
      <div style={{ flex: 1, position: "relative" }}>
        <MapContainer center={[3.139, 101.686]} zoom={10} style={{ height: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          
          {activeLayer && (
            <ImageOverlay 
              key={activeLayer}
              url={SiteService.getLayerUrl(activeLayer)} // Use service for URL
              bounds={LAYER_BOUNDS}
              opacity={0.6}
            />
          )}

          {selectedPosition && <Marker position={selectedPosition} />}
          <LocationSelector onSelect={setSelectedPosition} />
        </MapContainer>

        {/* Floating Controls */}
        <LayerControls active={activeLayer} onToggle={setActiveLayer} />
      </div>

      {/* 2. UI SECTION */}
      <div style={{ padding: "20px", textAlign: "center", borderTop: "2px solid #eee" }}>
        <button onClick={handlePredict} disabled={loading} style={btnStyle}>
          {loading ? "Analyzing..." : "Analyze Site"}
        </button>
        
        {data.prediction && (
          <div style={{ marginTop: "20px" }}>
            <h2 style={{ color: data.prediction === "Suitable" ? "green" : "red" }}>
              {data.prediction}
            </h2>
            <div style={insightGrid}>
              {data.insights.map((ins, i) => (
                <div key={i} style={{ ...insightCard, borderColor: getLevelColor(ins.level) }}>
                  {ins.text}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// --- Helper Components for Cleanliness ---

const LocationSelector = ({ onSelect }) => {
  useMapEvents({ click(e) { onSelect([e.latlng.lat, e.latlng.lng]); } });
  return null;
};

const LayerControls = ({ active, onToggle }) => (
  <div style={floatingPanel}>
    <button onClick={() => onToggle(active === 'population' ? null : 'population')}>
      {active === 'population' ? "Hide Population" : "Show Population"}
    </button>
    <button onClick={() => onToggle(active === 'landuse' ? null : 'landuse')}>
      {active === 'landuse' ? "Hide Landuse" : "Show Landuse"}
    </button>
  </div>
);

// --- Simple Styling Constants ---
const getLevelColor = (lvl) => lvl === 'danger' ? '#dc3545' : lvl === 'warning' ? '#ffc107' : '#28a745';
const btnStyle = { padding: "10px 20px", cursor: "pointer", background: "#007bff", color: "white", border: "none", borderRadius: "4px" };
const floatingPanel = { position: "absolute", top: 10, right: 10, zIndex: 1000, background: "white", padding: 10, borderRadius: 8, display: "flex", flexDirection: "column", gap: 5 };
const insightGrid = { display: "flex", justifyContent: "center", gap: 10, marginTop: 10 };
const insightCard = { padding: 10, background: "#f8f9fa", borderLeft: "5px solid", fontSize: "0.8em", width: "200px" };

export default App;