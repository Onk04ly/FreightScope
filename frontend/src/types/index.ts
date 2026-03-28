export type ShipmentStatus = "pending" | "processing" | "complete" | "failed";

export interface Shipment {
  id: number;
  origin_port: string;
  dest_port: string;
  carrier: string | null;
  status: ShipmentStatus;
  created_at: string;
}

export interface DelayForecastDay {
  date: string;
  p50: number;
  p90: number;
}

export interface RiskCard {
  id: number;
  shipment_id: number;
  fused_score: number | null;
  delay_days_p50: number | null;
  delay_days_p90: number | null;
  billing_anomaly_flag: boolean;
  damage_severity: "none" | "minor" | "moderate" | "severe" | null;
  ner_entities: Record<string, string[]> | null;
  incident_summary: string | null;
  delay_forecast: DelayForecastDay[] | null;
  created_at: string;
}

export type TaskState =
  | "PENDING"
  | "STARTED"
  | "PROGRESS"
  | "SUCCESS"
  | "FAILURE"
  | "RETRY";

export interface TaskStatus {
  task_id: string;
  state: TaskState;
  progress?: number;
  result?: unknown;
  error?: string;
}

export interface UploadResponse {
  shipment_id: number;
  task_ids: Record<string, string>;
  message: string;
}
