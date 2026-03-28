import { useState } from "react";
import { IncidentFeed } from "./components/IncidentFeed/IncidentFeed";
import { MapView } from "./components/MapView/MapView";
import { RiskCard } from "./components/RiskCard/RiskCard";
import { UploadZone } from "./components/UploadZone/UploadZone";
import { useShipments } from "./hooks/useShipments";
import type { Shipment } from "./types";

export default function App() {
  const [selectedShipment, setSelectedShipment] = useState<Shipment | null>(null);
  const { data: shipments = [] } = useShipments();

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>
      {/* Left sidebar */}
      <div style={{ width: 340, display: "flex", flexDirection: "column", borderRight: "1px solid #e2e8f0", overflowY: "auto" }}>
        <div style={{ padding: 16, borderBottom: "1px solid #e2e8f0" }}>
          <h1 style={{ margin: 0, fontSize: 20, fontWeight: 700 }}>FreightScope</h1>
          <p style={{ margin: "4px 0 0", fontSize: 12, color: "#64748b" }}>Multimodal logistics intelligence</p>
        </div>

        <div style={{ padding: 16, borderBottom: "1px solid #e2e8f0" }}>
          <UploadZone onUploaded={(shipmentId) => {
            const found = shipments.find((s) => s.id === shipmentId);
            if (found) setSelectedShipment(found);
          }} />
        </div>

        <div style={{ padding: 16, flex: 1 }}>
          <h2 style={{ fontSize: 14, fontWeight: 600, margin: "0 0 8px", color: "#475569" }}>SHIPMENTS</h2>
          {shipments.map((s) => (
            <div
              key={s.id}
              onClick={() => setSelectedShipment(s)}
              style={{
                padding: "8px 10px",
                marginBottom: 6,
                borderRadius: 6,
                cursor: "pointer",
                background: selectedShipment?.id === s.id ? "#eff6ff" : "#f8fafc",
                border: `1px solid ${selectedShipment?.id === s.id ? "#3b82f6" : "#e2e8f0"}`,
              }}
            >
              <div style={{ fontWeight: 600, fontSize: 13 }}>#{s.id} {s.origin_port} → {s.dest_port}</div>
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{s.carrier ?? "No carrier"} · {s.status}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        <MapView shipments={shipments} selectedShipment={selectedShipment} />

        {selectedShipment && (
          <div style={{ height: 260, display: "flex", borderTop: "1px solid #e2e8f0" }}>
            <div style={{ flex: 1, borderRight: "1px solid #e2e8f0", overflow: "auto" }}>
              <RiskCard shipmentId={selectedShipment.id} />
            </div>
            <div style={{ width: 300, overflow: "auto" }}>
              <IncidentFeed shipmentId={selectedShipment.id} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
