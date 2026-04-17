import { useState } from "react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import type { SensorReading, PaginatedResponse } from "@/types";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

const SENSOR_TYPES = ["temperature", "humidity", "co2", "occupancy"];
const COLORS = ["#2563eb", "#16a34a", "#ea580c", "#7c3aed"];

export default function SensorsPage() {
  const [buildingId, setBuildingId] = useState("");
  const [sensorType, setSensorType] = useState("temperature");

  const path = buildingId
    ? `/sensors/readings?building_id=${buildingId}&sensor_type=${sensorType}&limit=200`
    : null;
  const { data: readingsData, loading } =
    useApi<PaginatedResponse<SensorReading>>(path);
  const readings = readingsData?.items;

  const chartData = readings
    ?.slice()
    .reverse()
    .map((r) => ({
      time: new Date(r.time).toLocaleString([], {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      }),
      value: r.value,
      sensor: r.sensor_id,
    }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Sensor Data</h2>
          <p className="text-gray-500 text-sm mt-1">
            Real-time and historical sensor readings
          </p>
        </div>
        <div className="flex gap-3">
          <select
            value={sensorType}
            onChange={(e) => setSensorType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white focus:ring-2 focus:ring-primary-500 outline-none"
          >
            {SENSOR_TYPES.map((t) => (
              <option key={t} value={t}>
                {t.charAt(0).toUpperCase() + t.slice(1)}
              </option>
            ))}
          </select>
          <BuildingSelector value={buildingId} onChange={setBuildingId} />
        </div>
      </div>

      <Card title={`${sensorType.charAt(0).toUpperCase() + sensorType.slice(1)} Readings`}>
        {!buildingId ? (
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view sensor data
          </p>
        ) : loading ? (
          <Spinner />
        ) : chartData && chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={400}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="time" tick={{ fontSize: 10 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke={COLORS[SENSOR_TYPES.indexOf(sensorType)]}
                strokeWidth={2}
                dot={false}
                name={sensorType}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-gray-400 text-sm py-8 text-center">
            No readings found
          </p>
        )}
      </Card>

      {readings && readings.length > 0 && (
        <Card title="Recent Readings">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Time</th>
                  <th className="pb-2 font-medium">Sensor</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium text-right">Value</th>
                </tr>
              </thead>
              <tbody>
                {readings.slice(0, 20).map((r, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="py-2 text-gray-600">
                      {new Date(r.time).toLocaleString()}
                    </td>
                    <td className="py-2 font-mono text-xs">{r.sensor_id}</td>
                    <td className="py-2">{r.sensor_type}</td>
                    <td className="py-2 text-right font-medium">{r.value}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
