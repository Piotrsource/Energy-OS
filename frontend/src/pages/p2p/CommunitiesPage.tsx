import { useState } from "react";
import { Users, MapPin, Plus, BarChart3, Leaf } from "lucide-react";
import StatCard from "@/components/StatCard";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { EnergyCommunity, CommunityDashboard } from "@/types";

export default function CommunitiesPage() {
  const { data: communities, loading, refetch } = useApi<EnergyCommunity[]>("/p2p/communities");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const { data: dashboard } = useApi<CommunityDashboard>(
    selectedId ? `/p2p/communities/${selectedId}/dashboard` : null
  );

  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", lat: "", lng: "", radius_km: "5" });
  const [submitting, setSubmitting] = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post("/p2p/communities", {
        name: form.name,
        description: form.description || null,
        location_lat: parseFloat(form.lat),
        location_lng: parseFloat(form.lng),
        radius_km: parseFloat(form.radius_km),
        fee_discount_pct: 50,
      });
      refetch();
      setShowCreate(false);
      setForm({ name: "", description: "", lat: "", lng: "", radius_km: "5" });
    } catch {
      // handled by api client
    } finally {
      setSubmitting(false);
    }
  };

  const handleJoin = async (communityId: string) => {
    try {
      await api.post(`/p2p/communities/${communityId}/join`, {});
      refetch();
    } catch {
      // handled by api client
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Energy Communities</h2>
          <p className="text-gray-500 text-sm mt-1">Join or create local energy trading groups</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700"
        >
          <Plus className="w-4 h-4" /> Create Community
        </button>
      </div>

      {showCreate && (
        <Card title="Create Community">
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
              <input
                type="text"
                required
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. Maple Street Solar Co-op"
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                rows={2}
                placeholder="Optional description..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
              <input type="number" step="0.0001" required value={form.lat}
                onChange={(e) => setForm({ ...form, lat: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="40.7128" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
              <input type="number" step="0.0001" required value={form.lng}
                onChange={(e) => setForm({ ...form, lng: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" placeholder="-74.0060" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Radius (km)</label>
              <input type="number" step="0.5" min="0.5" required value={form.radius_km}
                onChange={(e) => setForm({ ...form, radius_km: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm" />
            </div>
            <div className="flex items-end gap-2">
              <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
              <button type="submit" disabled={submitting} className="px-4 py-2 text-sm bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 disabled:opacity-50">
                {submitting ? "Creating..." : "Create"}
              </button>
            </div>
          </form>
        </Card>
      )}

      {selectedId && dashboard && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard label="Members" value={dashboard.member_count} icon={<Users className="w-5 h-5" />} color="bg-purple-50 text-purple-600" />
          <StatCard label="Total Trades" value={dashboard.total_trades} icon={<BarChart3 className="w-5 h-5" />} color="bg-blue-50 text-blue-600" />
          <StatCard label="kWh Traded" value={`${dashboard.total_kwh_traded}`} icon={<MapPin className="w-5 h-5" />} color="bg-yellow-50 text-yellow-600" />
          <StatCard label="CO2 Avoided" value={`${dashboard.co2_avoided_kg} kg`} icon={<Leaf className="w-5 h-5" />} color="bg-green-50 text-green-600" />
        </div>
      )}

      <Card title="Communities">
        {loading ? <Spinner /> : (
          <div className="space-y-3">
            {communities?.length === 0 && (
              <p className="text-gray-400 text-sm text-center py-8">No communities yet. Create the first one!</p>
            )}
            {communities?.map((c) => (
              <div
                key={c.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedId === c.id ? "border-primary-500 bg-primary-50" : "hover:border-gray-300"
                }`}
                onClick={() => setSelectedId(selectedId === c.id ? null : c.id)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold">{c.name}</h4>
                    {c.description && <p className="text-sm text-gray-500 mt-1">{c.description}</p>}
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                      <span className="flex items-center gap-1"><Users className="w-3 h-3" />{c.member_count} members</span>
                      <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{c.radius_km} km radius</span>
                      <span>{c.fee_discount_pct}% fee discount</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleJoin(c.id); }}
                    className="px-3 py-1.5 bg-primary-600 text-white rounded-lg text-xs font-medium hover:bg-primary-700"
                  >
                    Join
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
