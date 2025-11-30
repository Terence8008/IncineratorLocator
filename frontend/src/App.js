// App.js
import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import axios from "axios";

// --- Controller: Handles API calls ---
const predictSuitability = async (lat, lng) => {
  try {
    const response = await axios.post("http://127.0.0.1:8000/api/predict", {
      latitude: lat,
      longitude: lng,
    });
    return response.data.prediction;
  } catch (err) {
    console.error("Prediction API error:", err);
    return null;
  }
};

// --- View Component for selecting location ---
const LocationSelector = ({ setSelectedPosition }) => {
  useMapEvents({
    click(e) {
      setSelectedPosition([e.latlng.lat, e.latlng.lng]);
    },
  });
  return null;
};

// --- Main App Component ---
function App() {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [prediction, setPrediction] = useState(null);

  const handlePredictClick = async () => {
    if (!selectedPosition) return alert("Please select a location first!");
    const result = await predictSuitability(
      selectedPosition[0],
      selectedPosition[1]
    );
    setPrediction(result);
  };

  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      <h1 style={{ textAlign: "center" }}>Incinerator Site Suitability</h1>
      <MapContainer
        center={[3.139, 101.686]} // Default Kuala Lumpur coords
        zoom={12}
        style={{ height: "80%", width: "100%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {selectedPosition && <Marker position={selectedPosition} />}
        <LocationSelector setSelectedPosition={setSelectedPosition} />
      </MapContainer>

      <div style={{ textAlign: "center", marginTop: "10px" }}>
        <button onClick={handlePredictClick}>Predict Suitability</button>
        {prediction !== null && <p>Prediction Result: {prediction}</p>}
      </div>
    </div>
  );
}

export default App;
