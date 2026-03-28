import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useRiskCard } from "../../hooks/useRiskCard";

const SEVERITY_COLOR: Record<string, string> = {
  none: "#22c55e",
  minor: "#84cc16",
  moderate: "#f59e0b",
  severe: "#ef4444",
};

function scoreColor(score: number | null): string {
  if (score === null) return "#94a3b8";
  if (score < 0.33) return "#22c55e";
  if (score < 0.66) return "#f59e0b";
  return "#ef4444";
}

interface Props {
  shipmentId: number;
}

export function RiskCard({ shipmentId }: Props) {
  const { data: risk, isLoading } = useRiskCard(shipmentId);

  if (isLoading) return <div style={{ padding: 16, color: "#94a3b8" }}>Loading risk data…</div>;
  if (!risk) return <div style={{ padding: 16, color: "#94a3b8" }}>No risk data yet.</div>;

  const score = risk.fused_score;
  const forecast = risk.delay_forecast ?? [];

  return (
    <div style={{ padding: 16 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
        <div
          style={{
            width: 52,
            height: 52,
            borderRadius: "50%",
            background: scoreColor(score),
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            color: "#fff",
            fontWeight: 700,
            fontSize: 15,
          }}
        >
          {score !== null ? Math.round(score * 100) : "—"}
        </div>
        <div>
          <div style={{ fontWeight: 600, fontSize: 14 }}>Risk Score</div>
          <div style={{ fontSize: 12, color: "#64748b" }}>
            Damage: <span style={{ color: SEVERITY_COLOR[risk.damage_severity ?? "none"] }}>{risk.damage_severity ?? "unknown"}</span>
            &nbsp;·&nbsp;Billing anomaly: {risk.billing_anomaly_flag ? "⚠️ Yes" : "✓ No"}
          </div>
        </div>
      </div>

      {forecast.length > 0 && (
        <div style={{ marginBottom: 12 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>7-Day Delay Forecast (days)</div>
          <ResponsiveContainer width="100%" height={80}>
            <LineChart data={forecast}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 10 }} width={24} />
              <Tooltip />
              <Line type="monotone" dataKey="p50" stroke="#3b82f6" dot={false} strokeWidth={2} name="P50" />
              <Line type="monotone" dataKey="p90" stroke="#f59e0b" dot={false} strokeWidth={1.5} strokeDasharray="4 2" name="P90" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {risk.billing_anomaly_flag && (
        <div style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "#475569", marginBottom: 4 }}>Billing Anomaly</div>
          <ResponsiveContainer width="100%" height={40}>
            <BarChart data={[{ name: "Amount", value: 100 }]}>
              <Bar dataKey="value" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
