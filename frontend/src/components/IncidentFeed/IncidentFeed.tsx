import { useRiskCard } from "../../hooks/useRiskCard";

const SEVERITY_BADGE: Record<string, { bg: string; text: string }> = {
  none: { bg: "#dcfce7", text: "#166534" },
  minor: { bg: "#d9f99d", text: "#3f6212" },
  moderate: { bg: "#fef9c3", text: "#854d0e" },
  severe: { bg: "#fee2e2", text: "#991b1b" },
};

interface Props {
  shipmentId: number;
}

export function IncidentFeed({ shipmentId }: Props) {
  const { data: risk } = useRiskCard(shipmentId);

  const incidents: Array<{ label: string; detail: string; severity: string }> = [];

  if (risk) {
    if (risk.billing_anomaly_flag) {
      incidents.push({ label: "Billing anomaly", detail: "Invoice amount exceeds route baseline", severity: "severe" });
    }
    if (risk.damage_severity && risk.damage_severity !== "none") {
      incidents.push({ label: "Cargo damage", detail: `Severity: ${risk.damage_severity}`, severity: risk.damage_severity });
    }
    if (risk.delay_days_p50 && risk.delay_days_p50 > 2) {
      incidents.push({ label: "Delay risk", detail: `Forecast P50: ${risk.delay_days_p50.toFixed(1)} days`, severity: risk.delay_days_p50 > 5 ? "severe" : "moderate" });
    }
    if (risk.ner_entities?.ORG?.length) {
      incidents.push({ label: "Carrier mention", detail: risk.ner_entities.ORG.slice(0, 3).join(", "), severity: "none" });
    }
    if (risk.incident_summary) {
      incidents.push({ label: "AI Summary", detail: risk.incident_summary, severity: "minor" });
    }
  }

  return (
    <div style={{ padding: 12 }}>
      <h2 style={{ fontSize: 13, fontWeight: 600, margin: "0 0 8px", color: "#475569" }}>INCIDENT FEED</h2>
      {incidents.length === 0 ? (
        <div style={{ fontSize: 12, color: "#94a3b8" }}>No incidents detected.</div>
      ) : (
        incidents.map((inc, i) => {
          const badge = SEVERITY_BADGE[inc.severity] ?? SEVERITY_BADGE.none;
          return (
            <div
              key={i}
              style={{
                padding: "7px 9px",
                marginBottom: 6,
                borderRadius: 5,
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontSize: 12, fontWeight: 600 }}>{inc.label}</span>
                <span style={{ fontSize: 10, padding: "2px 6px", borderRadius: 99, background: badge.bg, color: badge.text }}>
                  {inc.severity}
                </span>
              </div>
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>{inc.detail}</div>
            </div>
          );
        })
      )}
    </div>
  );
}
