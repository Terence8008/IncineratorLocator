// views/MapView.jsx
import { MapContainer, TileLayer, useMapEvents, Marker } from "react-leaflet";
import { useState } from "react";

export default function MapView({ onMapClick }) {
  const [marker, setMarker] = useState(null);

  function MapEvents() {
    useMapEvents({
      click(e) {
        const { lat, lng } = e.latlng;
        setMarker([lat, lng]);
        onMapClick({ lat, lon: lng });
      },
    });
    return null;
  }

  return (
    <MapContainer center={[3.139, 101.6869]} zoom={10} className="w-full h-full">
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <MapEvents />

      {marker && <Marker position={marker} />}
    </MapContainer>
  );
}
