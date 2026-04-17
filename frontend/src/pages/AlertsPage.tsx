import { useEffect, useState } from "react";
import { api } from "@/api/client";
import BuildingSelector from "@/components/BuildingSelector";
import type {
  PaginatedResponse,
  AlertRule,
  Alert,
  Zone,
} from "@/types";
import { Bell, BellOff, Check, Plus, Trash2, ToggleLeft, ToggleRight } from "lucide-react";

const SEVERITY_COLORS: Record<string, string> = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  high: "bg-orange-100 text-orange-800",
  critical: "bg-red-100 text-red-800",
};

export default function AlertsPage() {
  const [buildingId, setBuildingId] = useState("");
  const [rules, setRules] = useState<AlertRule[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [zones, setZones] = useState<Zone[]>([]);
  const [tab, setTab] = useState<"rules" | "alerts">("alerts");
  const [showCreate, setShowCreate] = useState(false);

  const [form, setForm] = useState({
    name: "",
    sensor_type: "temperature",
    condition: "gt",
    threshold: 30,
    severity: "medium",
    zone_id: "",
  });

  useEffect(() => {
    if (!buildingId) return;
    loadRules();
    loadAlerts();
    api.get<PaginatedResponse<Zone>>(`/zones/?building_id=${buildingId}&limit=200`)
      .then((r) => setZones(r.items));
  }, [buildingId]);

  const loadRules = () =>
    api.get<PaginatedResponse<AlertRule>>(`/alert-rules/?building_id=${buildingId}&limit=200`)
      .then((r) => setRules(r.items));

  const loadAlerts = () =>
    api.get<PaginatedResponse<Alert>>(`/alerts/?building_id=${buildingId}&limit=200`)
      .then((r) => setAlerts(r.items));

  const createRule = async () => {
    await api.post("/alert-rules/", {
      building_id: buildingId,
      zone_id: form.zone_id || null,
      sensor_type: form.sensor_type,
      condition: form.condition,
      threshold: form.threshold,
      severity: form.severity,
      name: form.name,
    });
    setShowCreate(false);
    loadRules();
  };

  const toggleRule = async (rule: AlertRule) => {
    await api.patch(`/alert-rules/${rule.id}`, { enabled: !rule.enabled });
    loadRules();
  };

  const deleteRule = async (id: string) => {
    await api.delete(`/alert-rules/${id}`);
    loadRules();
  };

  const acknowledgeAlert = async (id: string) => {
    await api.post(`/alerts/${id}/acknowledge`, {});
    loadAlerts();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Alerts & Rules</h1>
          <p className="text-sm text-gray-500 mt-1">Configure alert rules and view triggered alerts</p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      {!buildingId ? (
        <p className="text-gray-400">Select a building to view alerts.</p>
      ) : (
        <>
          <div className="flex gap-2">
            <button
              onClick={() => setTab("alerts")}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                tab === "alerts" ? "bg-red-600 text-white" : "bg-gray-200 text-gray-700"
              }`}
            >
              <Bell className="w-4 h-4 inline mr-1" />
              Alerts ({alerts.length})
            </button>
            <button
              onClick={() => setTab("rules")}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                tab === "rules" ? "bg-primary-600 text-white" : "bg-gray-200 text-gray-700"
              }`}
            >
              Rules ({rules.length})
            </button>
          </div>

          {tab === "alerts" && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              {alerts.length === 0 ? (
                <div className="p-8 text-center text-gray-400">
                  <BellOff className="w-12 h-12 mx-auto mb-3" />
                  <p>No alerts triggered yet</p>
                </div>
              ) : (
                <div className="divide-y">
                  {alerts.map((a) => {
                    const rule = rules.find((r) => r.id === a.rule_id);
                    return (
                      <div key={a.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                        <div>
                          <div className="flex items-center gap-2">
                            {rule && (
                              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${SEVERITY_COLORS[rule.severity]}`}>
                                {rule.severity}
                              </span>
                            )}
                            <span className="text-sm font-medium text-gray-800">
                              {rule?.name || rule?.sensor_type || "Unknown rule"} — value: {a.value}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            Sensor: {a.sensor_id} | {new Date(a.triggered_at).toLocaleString()}
                          </p>
                        </div>
                        {a.acknowledged_at ? (
                          <span className="text-xs text-green-600 font-medium">Acknowledged</span>
                        ) : (
                          <button
                            onClick={() => acknowledgeAlert(a.id)}
                            className="px-3 py-1.5 bg-green-100 text-green-700 text-xs rounded-lg hover:bg-green-200 flex items-center gap-1"
                          >
                            <Check className="w-3 h-3" /> Acknowledge
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {tab === "rules" && (
            <div className="space-y-4">
              <button
                onClick={() => setShowCreate(!showCreate)}
                className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium flex items-center gap-1 hover:bg-primary-700"
              >
                <Plus className="w-4 h-4" /> New Rule
              </button>

              {showCreate && (
                <div className="bg-white rounded-xl shadow-sm border p-5 space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
                      <input
                        value={form.name}
                        onChange={(e) => setForm({ ...form, name: e.target.value })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                        placeholder="e.g. High temperature lobby"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Sensor Type</label>
                      <select
                        value={form.sensor_type}
                        onChange={(e) => setForm({ ...form, sensor_type: e.target.value })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                      >
                        {["temperature", "humidity", "co2", "occupancy", "power", "light_level"].map((t) => (
                          <option key={t} value={t}>{t}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Condition</label>
                      <select
                        value={form.condition}
                        onChange={(e) => setForm({ ...form, condition: e.target.value })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                      >
                        {["gt", "lt", "eq", "gte", "lte"].map((c) => (
                          <option key={c} value={c}>{c === "gt" ? ">" : c === "lt" ? "<" : c === "eq" ? "=" : c === "gte" ? ">=" : "<="}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Threshold</label>
                      <input
                        type="number"
                        value={form.threshold}
                        onChange={(e) => setForm({ ...form, threshold: parseFloat(e.target.value) })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Severity</label>
                      <select
                        value={form.severity}
                        onChange={(e) => setForm({ ...form, severity: e.target.value })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                      >
                        {["low", "medium", "high", "critical"].map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-600 mb-1">Zone (optional)</label>
                      <select
                        value={form.zone_id}
                        onChange={(e) => setForm({ ...form, zone_id: e.target.value })}
                        className="w-full border rounded-lg px-3 py-2 text-sm"
                      >
                        <option value="">All zones</option>
                        {zones.map((z) => (
                          <option key={z.id} value={z.id}>{z.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={createRule} className="px-4 py-2 bg-primary-600 text-white rounded-lg text-sm">Create</button>
                    <button onClick={() => setShowCreate(false)} className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm">Cancel</button>
                  </div>
                </div>
              )}

              <div className="bg-white rounded-xl shadow-sm border divide-y">
                {rules.length === 0 ? (
                  <p className="p-8 text-center text-gray-400">No alert rules configured</p>
                ) : (
                  rules.map((r) => (
                    <div key={r.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${SEVERITY_COLORS[r.severity]}`}>
                            {r.severity}
                          </span>
                          <span className="text-sm font-medium">{r.name || `${r.sensor_type} ${r.condition} ${r.threshold}`}</span>
                          {!r.enabled && <span className="text-xs text-gray-400">(disabled)</span>}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">{r.sensor_type} {r.condition} {r.threshold}</p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button onClick={() => toggleRule(r)} className="text-gray-500 hover:text-primary-600">
                          {r.enabled ? <ToggleRight className="w-5 h-5 text-green-500" /> : <ToggleLeft className="w-5 h-5" />}
                        </button>
                        <button onClick={() => deleteRule(r.id)} className="text-gray-400 hover:text-red-600">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
