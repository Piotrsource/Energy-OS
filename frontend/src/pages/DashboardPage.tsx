import { useState, useMemo } from "react";
import {
  Building2,
  Thermometer,
  Zap,
  AlertTriangle,
  Wifi,
  WifiOff,
} from "lucide-react";
import StatCard from "@/components/StatCard";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import { useWebSocket } from "@/hooks/useWebSocket";
import type {
  Building,
  SensorReading,
  Recommendation,
  PaginatedResponse,
} from "@/types";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function DashboardPage() {
  const [buildingId, setBuildingId] = useState("");
  const { data: buildingsData } =
    useApi<PaginatedResponse<Building>>("/buildings?limit=500");
  const buildings = buildingsData?.items;

  // ── Historical readings (REST) ──────────────────────────────────────────
  const sensorPath = buildingId
    ? `/sensors/readings?building_id=${buildingId}&sensor_type=temperature&limit=96`
    : null;
  const { data: readingsData, loading: readingsLoading } =
    useApi<PaginatedResponse<SensorReading>>(sensorPath);
  const readings = readingsData?.items;

  // ── Live readings (WebSocket) ───────────────────────────────────────────
  const {
    lastReading,
    readings: liveReadings,
    connected: wsConnected,
  } = useWebSocket({ buildingId: buildingId || null });

  const recsPath = buildingId
    ? `/recommendations?building_id=${buildingId}`
    : null;
  const { data: recsData } =
    useApi<PaginatedResponse<Recommendation>>(recsPath);
  const recommendations = recsData?.items;

  // ── Merge historical + live readings for the chart ──────────────────────
  const chartData = useMemo(() => {
    // Start with historical readings (oldest first)
    const historical =
      readings
        ?.slice()
        .reverse()
        .map((r) => ({
          time: new Date(r.time).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
          value: r.value,
        })) ?? [];

    // Append live temperature readings (newest last)
    const live = liveReadings
      .filter((r) => r.sensor_type === "temperature")
      .reverse()
      .map((r) => ({
        time: new Date(r.time).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        value: r.value,
      }));

    // Deduplicate by time label — live readings take precedence
    const seen = new Set<string>();
    const merged: { time: string; value: number }[] = [];
    // Process live first so they overwrite historical
    for (const pt of live) seen.add(pt.time);
    for (const pt of historical) {
      if (!seen.has(pt.time)) {
        merged.push(pt);
        seen.add(pt.time);
      }
    }
    merged.push(...live);
    return merged;
  }, [readings, liveReadings]);

  // Latest temp from WebSocket or last REST reading
  const latestTemp =
    lastReading?.sensor_type === "temperature"
      ? lastReading.value
      : readings?.[0]?.value;

  const pendingRecs =
    recommendations?.filter((r) => r.status === "pending").length ?? 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Dashboard</h2>
          <p className="text-gray-500 text-sm mt-1">
            Real-time overview of your energy platform
          </p>
        </div>
        <div className="flex items-center gap-3">
          {buildingId && (
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                wsConnected
                  ? "bg-green-50 text-green-700"
                  : "bg-gray-100 text-gray-500"
              }`}
            >
              {wsConnected ? (
                <Wifi className="w-3.5 h-3.5" />
              ) : (
                <WifiOff className="w-3.5 h-3.5" />
              )}
              {wsConnected ? "Live" : "Connecting…"}
            </span>
          )}
          <BuildingSelector value={buildingId} onChange={setBuildingId} />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Buildings"
          value={buildings?.length ?? "..."}
          icon={<Building2 className="w-5 h-5" />}
        />
        <StatCard
          label="Latest Temp"
          value={latestTemp != null ? `${latestTemp}°C` : "—"}
          icon={<Thermometer className="w-5 h-5" />}
          color="bg-orange-50 text-orange-600"
        />
        <StatCard
          label="Pending Actions"
          value={pendingRecs}
          icon={<Zap className="w-5 h-5" />}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          label="Alerts"
          value={0}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="bg-red-50 text-red-600"
          trend="No anomalies detected"
        />
      </div>

      <Card title="Temperature (last 24h)">
        {!buildingId ? (
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view sensor data
          </p>
        ) : readingsLoading ? (
          <Spinner />
        ) : chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 11 }} />
              <YAxis
                domain={["auto", "auto"]}
                tick={{ fontSize: 11 }}
                unit="°C"
              />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400 text-sm py-8 text-center">
            No sensor data available
          </p>
        )}
      </Card>
    </div>
  );
}
