import { useEffect, useRef, useState, useCallback } from "react";
import type { SensorReading } from "@/types";

interface UseWebSocketOptions {
  /** Building ID to subscribe to. Pass empty string / null to disconnect. */
  buildingId: string | null;
  /** Max readings to buffer (oldest are dropped). Default 200. */
  bufferSize?: number;
}

interface UseWebSocketResult {
  /** Most recent reading from the WebSocket. */
  lastReading: SensorReading | null;
  /** Rolling buffer of recent readings (newest first). */
  readings: SensorReading[];
  /** true while the WebSocket is open. */
  connected: boolean;
}

/**
 * Hook that subscribes to the real-time sensor telemetry WebSocket.
 *
 * Connects to `/api/v1/sensors/ws/{buildingId}` via the Vite proxy,
 * auto-reconnects with exponential back-off, and exposes a rolling
 * buffer of the latest readings for live dashboard charts.
 */
export function useWebSocket({
  buildingId,
  bufferSize = 200,
}: UseWebSocketOptions): UseWebSocketResult {
  const [lastReading, setLastReading] = useState<SensorReading | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const timerRef = useRef<ReturnType<typeof setTimeout>>();
  const unmountedRef = useRef(false);

  const connect = useCallback(() => {
    if (!buildingId || unmountedRef.current) return;

    // Build WebSocket URL (works in both dev proxy and production)
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.host;
    const token = localStorage.getItem("token") ?? "";
    const url = `${proto}//${host}/api/v1/sensors/ws/${buildingId}?token=${token}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      if (unmountedRef.current) return;
      setConnected(true);
      retryRef.current = 0;
    };

    ws.onmessage = (event) => {
      if (unmountedRef.current) return;
      try {
        const reading: SensorReading = JSON.parse(event.data);
        setLastReading(reading);
        setReadings((prev) => [reading, ...prev].slice(0, bufferSize));
      } catch {
        // ignore malformed messages
      }
    };

    ws.onclose = () => {
      if (unmountedRef.current) return;
      setConnected(false);
      // Exponential back-off: 1s, 2s, 4s, 8s, …, max 30s
      const delay = Math.min(1000 * 2 ** retryRef.current, 30_000);
      retryRef.current += 1;
      timerRef.current = setTimeout(connect, delay);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [buildingId, bufferSize]);

  useEffect(() => {
    unmountedRef.current = false;
    setReadings([]);
    setLastReading(null);
    setConnected(false);
    retryRef.current = 0;

    connect();

    return () => {
      unmountedRef.current = true;
      clearTimeout(timerRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  return { lastReading, readings, connected };
}
