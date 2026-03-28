import { useEffect, useState } from "react";
import type { TaskStatus } from "../types";

const WS_BASE = `ws://${window.location.hostname}:8000`;

export function useTaskStatus(taskId: string | null): TaskStatus | null {
  const [status, setStatus] = useState<TaskStatus | null>(null);

  useEffect(() => {
    if (!taskId) return;

    const ws = new WebSocket(`${WS_BASE}/status/${taskId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as TaskStatus;
      setStatus(data);
      if (data.state === "SUCCESS" || data.state === "FAILURE") {
        ws.close();
      }
    };

    ws.onerror = () => ws.close();

    return () => {
      if (ws.readyState === WebSocket.OPEN) ws.close();
    };
  }, [taskId]);

  return status;
}
