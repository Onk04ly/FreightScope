import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useShipments(skip = 0, limit = 20) {
  return useQuery({
    queryKey: ["shipments", skip, limit],
    queryFn: () => api.getShipments(skip, limit),
    refetchInterval: 5000,
  });
}
