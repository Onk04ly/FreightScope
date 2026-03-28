import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useRiskCard(shipmentId: number | null) {
  return useQuery({
    queryKey: ["riskCard", shipmentId],
    queryFn: () => api.getRiskCard(shipmentId!),
    enabled: shipmentId !== null,
    refetchInterval: 3000,
  });
}
