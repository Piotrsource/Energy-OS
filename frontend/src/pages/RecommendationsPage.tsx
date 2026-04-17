import { useState } from "react";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import BuildingSelector from "@/components/BuildingSelector";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { Recommendation, PaginatedResponse } from "@/types";
import { CheckCircle, XCircle, Clock, Zap } from "lucide-react";

const STATUS_CONFIG: Record<string, { color: string; icon: typeof Clock }> = {
  pending: { color: "bg-yellow-100 text-yellow-800", icon: Clock },
  approved: { color: "bg-blue-100 text-blue-800", icon: CheckCircle },
  applied: { color: "bg-green-100 text-green-800", icon: CheckCircle },
  rejected: { color: "bg-red-100 text-red-800", icon: XCircle },
};

const TYPE_LABELS: Record<string, string> = {
  hvac_setpoint: "HVAC Setpoint",
  lighting_level: "Lighting Level",
  ventilation_rate: "Ventilation Rate",
  hvac_schedule: "HVAC Schedule",
};

export default function RecommendationsPage() {
  const [buildingId, setBuildingId] = useState("");

  const path = buildingId
    ? `/recommendations?building_id=${buildingId}`
    : null;
  const { data: recsData, loading, refetch } =
    useApi<PaginatedResponse<Recommendation>>(path);
  const recommendations = recsData?.items;

  const handleStatusUpdate = async (id: string, newStatus: string) => {
    try {
      await api.patch(`/recommendations/${id}`, { status: newStatus });
      refetch();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const pending = recommendations?.filter((r) => r.status === "pending") ?? [];
  const others = recommendations?.filter((r) => r.status !== "pending") ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Recommendations</h2>
          <p className="text-gray-500 text-sm mt-1">
            AI-generated optimization actions for your buildings
          </p>
        </div>
        <BuildingSelector value={buildingId} onChange={setBuildingId} />
      </div>

      {!buildingId ? (
        <Card>
          <p className="text-gray-400 text-sm py-8 text-center">
            Select a building to view recommendations
          </p>
        </Card>
      ) : loading ? (
        <Spinner />
      ) : (
        <>
          {pending.length > 0 && (
            <Card
              title={`Pending Actions (${pending.length})`}
              action={
                <span className="text-xs text-yellow-600 bg-yellow-50 px-2 py-1 rounded-full font-medium">
                  Needs review
                </span>
              }
            >
              <div className="space-y-3">
                {pending.map((rec) => (
                  <div
                    key={rec.id}
                    className="flex items-center justify-between p-4 bg-yellow-50 rounded-lg border border-yellow-100"
                  >
                    <div className="flex items-center gap-3">
                      <Zap className="w-5 h-5 text-yellow-600" />
                      <div>
                        <p className="font-medium text-sm">
                          {TYPE_LABELS[rec.recommendation_type] || rec.recommendation_type}
                        </p>
                        <p className="text-xs text-gray-500">
                          Set to {rec.value} | Created{" "}
                          {new Date(rec.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleStatusUpdate(rec.id, "approved")}
                        className="flex items-center gap-1 bg-green-600 text-white px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-green-700"
                      >
                        <CheckCircle className="w-3 h-3" />
                        Approve
                      </button>
                      <button
                        onClick={() => handleStatusUpdate(rec.id, "rejected")}
                        className="flex items-center gap-1 bg-red-100 text-red-700 px-3 py-1.5 rounded-lg text-xs font-medium hover:bg-red-200"
                      >
                        <XCircle className="w-3 h-3" />
                        Reject
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          <Card title="All Recommendations">
            {recommendations && recommendations.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-500 border-b">
                      <th className="pb-2 font-medium">Type</th>
                      <th className="pb-2 font-medium">Value</th>
                      <th className="pb-2 font-medium">Status</th>
                      <th className="pb-2 font-medium">Created</th>
                      <th className="pb-2 font-medium">Applied</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...pending, ...others].map((rec) => {
                      const cfg = STATUS_CONFIG[rec.status] || STATUS_CONFIG.pending;
                      return (
                        <tr key={rec.id} className="border-b border-gray-50">
                          <td className="py-2.5">
                            {TYPE_LABELS[rec.recommendation_type] || rec.recommendation_type}
                          </td>
                          <td className="py-2.5 font-medium">{rec.value}</td>
                          <td className="py-2.5">
                            <span
                              className={`inline-flex px-2 py-0.5 rounded-full text-xs font-medium ${cfg.color}`}
                            >
                              {rec.status}
                            </span>
                          </td>
                          <td className="py-2.5 text-gray-500">
                            {new Date(rec.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-2.5 text-gray-500">
                            {rec.applied_at
                              ? new Date(rec.applied_at).toLocaleDateString()
                              : "—"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-gray-400 text-sm py-8 text-center">
                No recommendations found
              </p>
            )}
          </Card>
        </>
      )}
    </div>
  );
}
