import { useEffect, useState } from "react";
import { api } from "@/api/client";
import BuildingSelector from "@/components/BuildingSelector";
import type { DeviceHealth } from "@/types";
import { Radio, Wifi, WifiOff } from "lucide-react";

const STATUS_STYLES: Record<string, { color: string; label: string }> = {
  online: { color: "bg-green-100 text-green-800", label: "Online" },
  stale:  { color: "bg-yellow-100 text-yellow-800", label: "Stale" },
  offline: { color: "bg-red-100 text-red-800", label: "Offline" },
};

export default function DeviceHealthPage() {
  const [buildingId, setBuildingId] = useState("");
  const [health, setHealth] = useState<DeviceHealth[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!buildingId) return;
    setLoading(true);
    api.get<{ items: DeviceHealth[] }>(`/sensors/health?building_id=${buildingId}`)
      .then((r) => setHealth(r.items))
      .catch(() => setHealth([]))
      .finally(() => setLoading(false));
  }, [buildingId]);

  const online = health.filter((h) => h.status === "online").length;
  const stale = health.filter((h) => h.status === "stale").length;
  const offline = health.filter((h) => h.status === "offline").length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Device Health</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor sensor connectivity and staleness</p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      {!buildingId ? (
        <p className="text-gray-400">Select a building to view device health.</p>
      ) : loading ? (
        <p className="text-gray-400">Loading...</p>
      ) : (
        <>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
              <Wifi className="w-6 h-6 text-green-600 mx-auto" />
              <p className="text-2xl font-bold text-green-700 mt-1">{online}</p>
              <p className="text-xs text-green-600">Online (&lt;5 min)</p>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
              <Radio className="w-6 h-6 text-yellow-600 mx-auto" />
              <p className="text-2xl font-bold text-yellow-700 mt-1">{stale}</p>
              <p className="text-xs text-yellow-600">Stale (5–30 min)</p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
              <WifiOff className="w-6 h-6 text-red-600 mx-auto" />
              <p className="text-2xl font-bold text-red-700 mt-1">{offline}</p>
              <p className="text-xs text-red-600">Offline (&gt;30 min)</p>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm border">
            {health.length === 0 ? (
              <p className="p-8 text-center text-gray-400">No cached devices found. Insert sensor readings to populate.</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Sensor ID</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Last Value</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Last Seen</th>
                    <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {health.map((h) => {
                    const style = STATUS_STYLES[h.status];
                    return (
                      <tr key={h.sensor_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-mono text-xs">{h.sensor_id}</td>
                        <td className="px-4 py-3">{h.sensor_type}</td>
                        <td className="px-4 py-3 font-medium">{h.last_value.toFixed(2)}</td>
                        <td className="px-4 py-3 text-gray-500">{new Date(h.last_seen).toLocaleString()}</td>
                        <td className="px-4 py-3">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${style.color}`}>{style.label}</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}
