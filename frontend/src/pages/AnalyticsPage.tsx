import { useState, useMemo } from "react";
import Card from "@/components/Card";
import StatCard from "@/components/StatCard";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import type { EnergySummary, CarbonEmissions, AnomalyRecord } from "@/types";
import { Zap, Leaf, AlertTriangle } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
} from "recharts";

export default function AnalyticsPage() {
  const [buildingId, setBuildingId] = useState("");

  const now = useMemo(() => new Date().toISOString(), []);
  const weekAgo = useMemo(
    () => new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    []
  );

  const energyPath = buildingId
    ? `/buildings/${buildingId}/energy-summary?start=${weekAgo}&end=${now}`
    : null;
  const carbonPath = buildingId
    ? `/buildings/${buildingId}/carbon-emissions?start=${weekAgo}&end=${now}`
    : null;
  const anomalyPath = buildingId
    ? `/anomalies?building_id=${buildingId}`
    : null;

  const { data: energy, loading: energyLoading } =
    useApi<EnergySummary>(energyPath);
  const { data: carbon, loading: carbonLoading } =
    useApi<CarbonEmissions>(carbonPath);
  const { data: anomalies, loading: anomaliesLoading } =
    useApi<AnomalyRecord[]>(anomalyPath);

  const energyChartData = energy?.buckets.map((b) => ({
    time: new Date(b.bucket).toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
    }),
    kWh: b.total_kwh,
    peak: b.peak_kwh,
  }));

  const carbonChartData = carbon?.buckets.map((b) => ({
    time: new Date(b.bucket).toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
    }),
    carbon: b.carbon_kg,
  }));

  const severityColors: Record<string, string> = {
    critical: "bg-red-100 text-red-800",
    high: "bg-orange-100 text-orange-800",
    medium: "bg-yellow-100 text-yellow-800",
    low: "bg-blue-100 text-blue-800",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Analytics</h2>
          <p className="text-gray-500 text-sm mt-1">
            Energy consumption, carbon emissions, and anomaly detection
          </p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      {!buildingId ? (
        <Card>
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view analytics
          </p>
        </Card>
      ) : (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <StatCard
              label="Total Energy (7d)"
              value={energy ? `${energy.total_kwh.toLocaleString()} kWh` : "..."}
              icon={<Zap className="w-5 h-5" />}
              color="bg-yellow-50 text-yellow-600"
            />
            <StatCard
              label="Carbon Emissions (7d)"
              value={
                carbon
                  ? `${carbon.total_carbon_kg.toLocaleString()} kg CO2`
                  : "..."
              }
              icon={<Leaf className="w-5 h-5" />}
              color="bg-green-50 text-green-600"
            />
            <StatCard
              label="Anomalies Detected"
              value={anomalies?.length ?? "..."}
              icon={<AlertTriangle className="w-5 h-5" />}
              color="bg-red-50 text-red-600"
            />
          </div>

          <Card title="Energy Consumption (kWh per hour)">
            {energyLoading ? (
              <Spinner />
            ) : energyChartData && energyChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={energyChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar
                    dataKey="kWh"
                    fill="#2563eb"
                    radius={[4, 4, 0, 0]}
                    name="Total kWh"
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-sm py-8 text-center">
                No energy data available
              </p>
            )}
          </Card>

          <Card title="Carbon Emissions (kg CO2 per hour)">
            {carbonLoading ? (
              <Spinner />
            ) : carbonChartData && carbonChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={280}>
                <LineChart data={carbonChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="time" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line
                    type="monotone"
                    dataKey="carbon"
                    stroke="#16a34a"
                    strokeWidth={2}
                    dot={false}
                    name="CO2 (kg)"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-gray-400 text-sm py-8 text-center">
                No carbon data available
              </p>
            )}
          </Card>

          <Card title="Anomalies">
            {anomaliesLoading ? (
              <Spinner />
            ) : anomalies && anomalies.length > 0 ? (
              <div className="space-y-2">
                {anomalies.map((a) => (
                  <div
                    key={a.id}
                    className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 border border-gray-100"
                  >
                    <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                            severityColors[a.severity]
                          }`}
                        >
                          {a.severity}
                        </span>
                        <span className="text-xs text-gray-400">
                          {new Date(a.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="text-sm text-gray-700 mt-1">
                        {a.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 text-sm py-8 text-center">
                No anomalies detected
              </p>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
