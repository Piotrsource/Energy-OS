import { useState } from "react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { Building, PaginatedResponse } from "@/types";
import { Plus, Trash2, MapPin } from "lucide-react";

export default function BuildingsPage() {
  const { data, loading, refetch } = useApi<PaginatedResponse<Building>>("/buildings?limit=500");
  const buildings = data?.items;
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: "", address: "", type: "hotel", timezone: "UTC" });
  const [saving, setSaving] = useState(false);

  const handleCreate = async () => {
    setSaving(true);
    try {
      await api.post("/buildings", form);
      setShowForm(false);
      setForm({ name: "", address: "", type: "hotel", timezone: "UTC" });
      refetch();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this building and all its zones?")) return;
    try {
      await api.delete(`/buildings/${id}`);
      refetch();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Buildings</h2>
          <p className="text-gray-500 text-sm mt-1">
            Manage buildings in the platform
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Add Building
        </button>
      </div>

      {showForm && (
        <Card title="New Building">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              placeholder="Building name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <input
              placeholder="Address"
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            />
            <select
              value={form.type}
              onChange={(e) => setForm({ ...form, type: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            >
              <option value="hotel">Hotel</option>
              <option value="office">Office</option>
              <option value="retail">Retail</option>
              <option value="hospital">Hospital</option>
            </select>
            <input
              placeholder="Timezone (e.g. America/New_York)"
              value={form.timezone}
              onChange={(e) => setForm({ ...form, timezone: e.target.value })}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <div className="mt-4 flex gap-2">
            <button
              onClick={handleCreate}
              disabled={saving || !form.name || !form.address}
              className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50"
            >
              {saving ? "Creating..." : "Create"}
            </button>
            <button
              onClick={() => setShowForm(false)}
              className="border border-gray-300 px-4 py-2 rounded-lg text-sm text-gray-600 hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </Card>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {buildings?.map((b) => (
          <div
            key={b.id}
            className="bg-white rounded-xl border border-gray-200 shadow-sm p-5 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900">{b.name}</h3>
                <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                  <MapPin className="w-3 h-3" />
                  {b.address}
                </p>
              </div>
              <button
                onClick={() => handleDelete(b.id)}
                className="text-gray-400 hover:text-red-500 transition-colors p-1"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            <div className="mt-3 flex gap-2">
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                {b.type}
              </span>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                {b.timezone}
              </span>
            </div>
          </div>
        ))}
      </div>

      {buildings?.length === 0 && (
        <p className="text-gray-400 text-center py-12">
          No buildings yet. Create one to get started.
        </p>
      )}
    </div>
  );
}
