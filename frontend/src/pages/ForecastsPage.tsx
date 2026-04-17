import { useState } from "react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import type { Forecast, PaginatedResponse } from "@/types";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

export default function ForecastsPage() {
  const [buildingId, setBuildingId] = useState("");

  const path = buildingId ? `/forecasts?building_id=${buildingId}` : null;
  const { data: forecastsData, loading } =
    useApi<PaginatedResponse<Forecast>>(path);
  const forecasts = forecastsData?.items;

  const chartData = forecasts
    ?.slice()
    .sort((a, b) => a.forecast_time.localeCompare(b.forecast_time))
    .map((f) => ({
      time: new Date(f.forecast_time).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
      }),
      predicted: f.predicted_value,
      type: f.forecast_type,
    }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">AI Forecasts</h2>
          <p className="text-gray-500 text-sm mt-1">
            AI-generated energy consumption predictions
          </p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      <Card title="Energy Consumption Forecast">
        {!buildingId ? (
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view forecasts
          </p>
        ) : loading ? (
          <Spinner />
        ) : chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Area
                type="monotone"
                dataKey="predicted"
                stroke="#2563eb"
                strokeWidth={2}
                fill="url(#colorPred)"
                name="Predicted Value"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400 text-sm py-8 text-center">
            No forecasts available
          </p>
        )}
      </Card>
    </div>
  );
}
