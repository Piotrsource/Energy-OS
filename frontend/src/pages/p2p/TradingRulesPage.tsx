import { useState } from "react";
import { Bot, Plus, Power, Trash2, Play } from "lucide-react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { TradingRule } from "@/types";

export default function TradingRulesPage() {
  const { data: rules, loading, refetch } = useApi<TradingRule[]>("/p2p/trading-rules");
  const [showCreate, setShowCreate] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    rule_type: "auto_sell" as "auto_sell" | "auto_buy",
    description: "",
    min_price: "12",
    max_quantity_kwh: "10",
    time_from: "16:00",
    time_until: "20:00",
    battery_threshold: "80",
  });

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/p2p/trading-rules", {
        rule_type: form.rule_type,
        description: form.description || `Auto-${form.rule_type === "auto_sell" ? "sell" : "buy"} rule`,
        conditions_json: {
          battery_above_pct: form.rule_type === "auto_sell" ? parseInt(form.battery_threshold) : undefined,
          price_above_cents: form.rule_type === "auto_sell" ? parseInt(form.min_price) : undefined,
          price_below_cents: form.rule_type === "auto_buy" ? parseInt(form.min_price) : undefined,
          time_window: { from: form.time_from, until: form.time_until },
        },
        action_json: {
          quantity_wh: Math.round(parseFloat(form.max_quantity_kwh) * 1000),
          price_cents_per_kwh: parseInt(form.min_price),
        },
        enabled: true,
      });
      refetch();
      setShowCreate(false);
    } catch {
      // handled by api client
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggle = async (rule: TradingRule) => {
    try {
      await api.patch(`/p2p/trading-rules/${rule.id}`, { enabled: !rule.enabled });
      refetch();
    } catch {
      // handled by api client
    }
  };

  const handleDelete = async (ruleId: string) => {
    try {
      await api.delete(`/p2p/trading-rules/${ruleId}`);
      refetch();
    } catch {
      // handled by api client
    }
  };

  const handleTest = async (ruleId: string) => {
    try {
      const result = await api.post<{ would_trigger: boolean; reason: string }>(
        `/p2p/trading-rules/${ruleId}/test`, {}
      );
      alert(`Would trigger: ${result.would_trigger}\nReason: ${result.reason}`);
    } catch {
      // handled by api client
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Automated Trading Rules</h2>
          <p className="text-gray-500 text-sm mt-1">Set rules to automatically create offers and requests</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" /> New Rule
        </button>
      </div>

      {showCreate && (
        <Card title="Create Trading Rule">
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="flex gap-4">
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="rule_type"
                  checked={form.rule_type === "auto_sell"}
                  onChange={() => setForm({ ...form, rule_type: "auto_sell" })}
                />
                <span className="text-sm font-medium text-green-700">Auto-Sell</span>
              </label>
              <label className="flex items-center gap-2">
                <input
                  type="radio"
                  name="rule_type"
                  checked={form.rule_type === "auto_buy"}
                  onChange={() => setForm({ ...form, rule_type: "auto_buy" })}
                />
                <span className="text-sm font-medium text-blue-700">Auto-Buy</span>
              </label>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {form.rule_type === "auto_sell" ? "Min Price (¢/kWh)" : "Max Price (¢/kWh)"}
                </label>
                <input type="number" min="1" required value={form.min_price}
                  onChange={(e) => setForm({ ...form, min_price: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Max Quantity (kWh)</label>
                <input type="number" step="0.1" min="0.1" required value={form.max_quantity_kwh}
                  onChange={(e) => setForm({ ...form, max_quantity_kwh: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>
              {form.rule_type === "auto_sell" && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Battery Threshold (%)</label>
                  <input type="number" min="0" max="100" required value={form.battery_threshold}
                    onChange={(e) => setForm({ ...form, battery_threshold: e.target.value })}
                    className="w-full border rounded-lg px-3 py-2 text-sm" />
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Active From</label>
                <input type="time" required value={form.time_from}
                  onChange={(e) => setForm({ ...form, time_from: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Active Until</label>
                <input type="time" required value={form.time_until}
                  onChange={(e) => setForm({ ...form, time_until: e.target.value })}
                  className="w-full border rounded-lg px-3 py-2 text-sm" />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description (optional)</label>
              <input type="text" value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. Sell excess when battery is above 80% between 4-8 PM" />
            </div>

            <div className="flex gap-2 justify-end">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
                {submitting ? "Creating..." : "Create Rule"}
              </button>
            </div>
          </form>
        </Card>
      )}

      <Card title={`Active Rules (${rules?.length ?? 0})`}>
        {loading ? <Spinner /> : (
          <div className="space-y-3">
            {rules?.length === 0 && (
              <p className="text-gray-400 text-sm text-center py-8">No trading rules. Create one to automate your trading!</p>
            )}
            {rules?.map((rule) => (
              <div key={rule.id} className={`border rounded-lg p-4 ${rule.enabled ? "border-green-200 bg-green-50/30" : "border-gray-200 bg-gray-50/50 opacity-75"}`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Bot className={`w-5 h-5 ${rule.rule_type === "auto_sell" ? "text-green-600" : "text-blue-600"}`} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          rule.rule_type === "auto_sell" ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
                        }`}>
                          {rule.rule_type === "auto_sell" ? "Auto-Sell" : "Auto-Buy"}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                          rule.enabled ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-500"
                        }`}>
                          {rule.enabled ? "Active" : "Disabled"}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">{rule.description ?? "No description"}</p>
                      {rule.last_triggered_at && (
                        <p className="text-xs text-gray-400 mt-1">Last triggered: {new Date(rule.last_triggered_at).toLocaleString()}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-1">
                    <button onClick={() => handleTest(rule.id)} title="Test rule"
                      className="p-2 text-gray-400 hover:text-blue-600 rounded-lg hover:bg-blue-50">
                      <Play className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleToggle(rule)} title={rule.enabled ? "Disable" : "Enable"}
                      className={`p-2 rounded-lg ${rule.enabled ? "text-green-600 hover:bg-green-50" : "text-gray-400 hover:bg-gray-100"}`}>
                      <Power className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDelete(rule.id)} title="Delete"
                      className="p-2 text-gray-400 hover:text-red-600 rounded-lg hover:bg-red-50">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
