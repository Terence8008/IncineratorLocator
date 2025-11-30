import React, { useState } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import axios from "axios";

// Fix default marker icon issue in Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

export default function HomeView() {
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  // Map click handler
  function MapClickHandler() {
    useMapEvents({
      click(e) {
        setSelectedPosition([e.latlng.lat, e.latlng.lng]);
        setPrediction(null); // clear previous prediction
      },
    });
    return null;
  }

  // Call backend API
  const handlePredict = async () => {
    if (!selectedPosition) return;
    setLoading(true);
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/predict",
        {
          lat: selectedPosition[0],
          lon: selectedPosition[1],
        }
      );
      setPrediction(response.data.prediction);
    } catch (error) {
      console.error("Prediction error:", error);
      setPrediction("Error fetching prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", height: "100vh" }}>
      {/* Sidebar */}
      <div
        style={{
          width: "300px",
          padding: "20px",
          backgroundColor: "#f2f2f2",
          boxShadow: "2px 0 5px rgba(0,0,0,0.1)",
        }}
      >
        <h2>Incinerator Site Selection</h2>
        {selectedPosition ? (
          <>
            <p>
              Selected Position: <br />
              Lat: {selectedPosition[0].toFixed(6)} <br />
              Lon: {selectedPosition[1].toFixed(6)}
            </p>
            <button onClick={handlePredict} disabled={loading}>
              {loading ? "Predicting..." : "Predict Suitability"}
            </button>
            {prediction !== null && (
              <div style={{ marginTop: "20px" }}>
                <strong>Prediction:</strong> {prediction}
              </div>
            )}
          </>
        ) : (
          <p>Click on the map to select a location.</p>
        )}
      </div>

      {/* Map */}
      <MapContainer
        center={[3.1390, 101.6869]} // Default: Kuala Lumpur
        zoom={10}
        style={{ flex: 1 }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        <MapClickHandler />
        {selectedPosition && <Marker position={selectedPosition} />}
      </MapContainer>
    </div>
  );
}
    