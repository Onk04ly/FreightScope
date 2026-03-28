import "leaflet/dist/leaflet.css";
import { MapContainer, CircleMarker, Polyline, TileLayer, Tooltip } from "react-leaflet";
import type { Shipment } from "../../types";

// Rough port coordinate lookup (extend as needed)
const PORT_COORDS: Record<string, [number, number]> = {
  "Shanghai": [31.23, 121.47],
  "Singapore": [1.29, 103.85],
  "Rotterdam": [51.92, 4.48],
  "Los Angeles": [33.74, -118.27],
  "Dubai": [25.20, 55.27],
  "Hamburg": [53.55, 9.99],
  "Busan": [35.10, 129.04],
  "New York": [40.69, -74.04],
  "Antwerp": [51.23, 4.41],
  "Ningbo": [29.87, 121.54],
};

function scoreToColor(score: number | null): string {
  if (score === null) return "#94a3b8";
  if (score < 0.33) return "#22c55e";
  if (score < 0.66) return "#f59e0b";
  return "#ef4444";
}

interface Props {
  shipments: Shipment[];
  selectedShipment: Shipment | null;
}

export function MapView({ shipments, selectedShipment }: Props) {
  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      style={{ flex: 1, minHeight: 0 }}
      scrollWheelZoom
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {shipments.map((s) => {
        const origin = PORT_COORDS[s.origin_port];
        const dest = PORT_COORDS[s.dest_port];
        const isSelected = selectedShipment?.id === s.id;
        const color = isSelected ? "#3b82f6" : "#94a3b8";

        return (
          <div key={s.id}>
            {origin && dest && (
              <Polyline
                positions={[origin, dest]}
                pathOptions={{ color, weight: isSelected ? 3 : 1.5, dashArray: isSelected ? undefined : "4 4" }}
              />
            )}
            {origin && (
              <CircleMarker center={origin} radius={5} pathOptions={{ color: "#1e40af", fillColor: "#3b82f6", fillOpacity: 0.8 }}>
                <Tooltip>{s.origin_port}</Tooltip>
              </CircleMarker>
            )}
            {dest && (
              <CircleMarker center={dest} radius={5} pathOptions={{ color: "#166534", fillColor: "#22c55e", fillOpacity: 0.8 }}>
                <Tooltip>{s.dest_port}</Tooltip>
              </CircleMarker>
            )}
          </div>
        );
      })}
    </MapContainer>
  );
}
