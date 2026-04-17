import { useState } from "react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import type { HvacStatus, PaginatedResponse } from "@/types";

const STATUS_COLORS: Record<string, string> = {
  running: "bg-green-100 text-green-800",
  idle: "bg-yellow-100 text-yellow-800",
  off: "bg-gray-100 text-gray-600",
  fault: "bg-red-100 text-red-800",
  maintenance: "bg-blue-100 text-blue-800",
};

export default function HvacPage() {
  const [buildingId, setBuildingId] = useState("");

  const path = buildingId
    ? `/hvac/status?building_id=${buildingId}&limit=100`
    : null;
  const { data: hvacData, loading } =
    useApi<PaginatedResponse<HvacStatus>>(path);
  const entries = hvacData?.items;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">HVAC Status</h2>
          <p className="text-gray-500 text-sm mt-1">
            Monitor heating, ventilation and air conditioning equipment
          </p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      <Card title="Status History">
        {!buildingId ? (
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view HVAC status
          </p>
        ) : loading ? (
          <Spinner />
        ) : entries && entries.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Time</th>
                  <th className="pb-2 font-medium">Device</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium">Status</th>
                  <th className="pb-2 font-medium text-right">Setpoint</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((e, i) => (
                  <tr key={i} className="border-b border-gray-50">
                    <td className="py-2 text-gray-600">
                      {new Date(e.time).toLocaleString()}
                    </td>
                    <td className="py-2 font-mono text-xs">{e.device_id}</td>
                    <td className="py-2">{e.device_type.toUpperCase()}</td>
                    <td className="py-2">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${
                          STATUS_COLORS[e.status] || "bg-gray-100 text-gray-600"
                        }`}
                      >
                        {e.status}
                      </span>
                    </td>
                    <td className="py-2 text-right font-medium">
                      {e.setpoint != null ? `${e.setpoint}°C` : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-400 text-sm py-8 text-center">
            No HVAC data found
          </p>
        )}
      </Card>
    </div>
  );
}
