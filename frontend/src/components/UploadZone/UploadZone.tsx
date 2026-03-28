import { useRef, useState } from "react";
import { api } from "../../api/client";
import { useTaskStatus } from "../../hooks/useTaskStatus";

interface Props {
  onUploaded: (shipmentId: number) => void;
}

export function UploadZone({ onUploaded }: Props) {
  const [originPort, setOriginPort] = useState("");
  const [destPort, setDestPort] = useState("");
  const [carrier, setCarrier] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const invoiceRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLInputElement>(null);
  const noteRef = useRef<HTMLInputElement>(null);

  const taskStatus = useTaskStatus(taskId);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    const fd = new FormData();
    fd.append("origin_port", originPort);
    fd.append("dest_port", destPort);
    fd.append("carrier", carrier);
    if (invoiceRef.current?.files?.[0]) fd.append("invoice", invoiceRef.current.files[0]);
    if (imageRef.current?.files?.[0]) fd.append("cargo_image", imageRef.current.files[0]);
    if (noteRef.current?.files?.[0]) fd.append("carrier_note", noteRef.current.files[0]);

    try {
      const res = await api.uploadShipment(fd);
      const firstTaskId = Object.values(res.task_ids)[0] ?? null;
      setTaskId(firstTaskId);
      onUploaded(res.shipment_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  const inputStyle: React.CSSProperties = {
    width: "100%",
    padding: "5px 8px",
    border: "1px solid #e2e8f0",
    borderRadius: 4,
    fontSize: 12,
    boxSizing: "border-box",
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2 style={{ fontSize: 13, fontWeight: 600, margin: "0 0 8px", color: "#475569" }}>NEW SHIPMENT</h2>

      <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
        <input style={inputStyle} placeholder="Origin port" value={originPort} onChange={(e) => setOriginPort(e.target.value)} required />
        <input style={inputStyle} placeholder="Dest port" value={destPort} onChange={(e) => setDestPort(e.target.value)} required />
      </div>
      <input style={{ ...inputStyle, marginBottom: 6 }} placeholder="Carrier (optional)" value={carrier} onChange={(e) => setCarrier(e.target.value)} />

      <div style={{ marginBottom: 6, fontSize: 11, color: "#64748b" }}>
        <label style={{ display: "block", marginBottom: 3 }}>
          Invoice PDF <input ref={invoiceRef} type="file" accept=".pdf" style={{ fontSize: 11 }} />
        </label>
        <label style={{ display: "block", marginBottom: 3 }}>
          Cargo image <input ref={imageRef} type="file" accept="image/*" style={{ fontSize: 11 }} />
        </label>
        <label style={{ display: "block" }}>
          Carrier note <input ref={noteRef} type="file" accept=".txt,.pdf" style={{ fontSize: 11 }} />
        </label>
      </div>

      {error && <div style={{ fontSize: 11, color: "#ef4444", marginBottom: 6 }}>{error}</div>}

      {taskStatus && (
        <div style={{ fontSize: 11, color: "#64748b", marginBottom: 6 }}>
          Processing: <strong>{taskStatus.state}</strong>
        </div>
      )}

      <button
        type="submit"
        disabled={submitting}
        style={{
          width: "100%",
          padding: "7px 0",
          background: submitting ? "#94a3b8" : "#3b82f6",
          color: "#fff",
          border: "none",
          borderRadius: 4,
          fontSize: 13,
          fontWeight: 600,
          cursor: submitting ? "default" : "pointer",
        }}
      >
        {submitting ? "Uploading…" : "Upload & Analyse"}
      </button>
    </form>
  );
}
