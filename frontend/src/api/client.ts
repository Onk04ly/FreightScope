import type { RiskCard, Shipment, UploadResponse } from "../types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  getShipments: (skip = 0, limit = 20) =>
    request<Shipment[]>(`/shipments?skip=${skip}&limit=${limit}`),

  getRiskCard: (shipmentId: number) =>
    request<RiskCard>(`/risk/${shipmentId}`),

  uploadShipment: (formData: FormData) =>
    request<UploadResponse>("/upload", { method: "POST", body: formData }),
};
