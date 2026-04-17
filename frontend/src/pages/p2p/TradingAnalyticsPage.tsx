import { DollarSign, Zap, TrendingUp, TrendingDown, Leaf, BarChart3 } from "lucide-react";
import StatCard from "@/components/StatCard";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import type { SellerAnalytics, BuyerAnalytics, P2POrder } from "@/types";

function formatCents(cents: number) {
  return `$${(Math.abs(cents) / 100).toFixed(2)}`;
}

export default function TradingAnalyticsPage() {
  const { data: sellerStats, loading: sellerLoading } = useApi<SellerAnalytics>("/p2p/analytics/seller");
  const { data: buyerStats, loading: buyerLoading } = useApi<BuyerAnalytics>("/p2p/analytics/buyer");
  const { data: orders } = useApi<P2POrder[]>("/p2p/orders?limit=10");

  if (sellerLoading || buyerLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Trading Analytics</h2>
        <p className="text-gray-500 text-sm mt-1">Your P2P energy trading performance</p>
      </div>

      <h3 className="text-lg font-semibold text-green-700 flex items-center gap-2">
        <TrendingUp className="w-5 h-5" /> Seller Performance
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Revenue"
          value={sellerStats ? formatCents(sellerStats.total_revenue_cents) : "—"}
          icon={<DollarSign className="w-5 h-5" />}
          color="bg-green-50 text-green-600"
        />
        <StatCard
          label="kWh Sold"
          value={sellerStats?.total_kwh_sold ?? "—"}
          icon={<Zap className="w-5 h-5" />}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          label="Avg Sell Price"
          value={sellerStats ? `${sellerStats.avg_sell_price_cents_per_kwh}¢/kWh` : "—"}
          icon={<TrendingUp className="w-5 h-5" />}
          color="bg-blue-50 text-blue-600"
        />
        <StatCard
          label="Monthly Projection"
          value={sellerStats ? formatCents(sellerStats.earnings_projection_monthly_cents) : "—"}
          icon={<BarChart3 className="w-5 h-5" />}
          trend={sellerStats ? `${sellerStats.active_offers} active offers` : undefined}
        />
      </div>

      <h3 className="text-lg font-semibold text-blue-700 flex items-center gap-2">
        <TrendingDown className="w-5 h-5" /> Buyer Performance
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Spent"
          value={buyerStats ? formatCents(buyerStats.total_spent_cents) : "—"}
          icon={<DollarSign className="w-5 h-5" />}
          color="bg-red-50 text-red-600"
        />
        <StatCard
          label="kWh Bought"
          value={buyerStats?.total_kwh_bought ?? "—"}
          icon={<Zap className="w-5 h-5" />}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          label="Savings vs Grid"
          value={buyerStats ? formatCents(buyerStats.savings_vs_grid_cents) : "—"}
          icon={<TrendingDown className="w-5 h-5" />}
          color="bg-green-50 text-green-600"
        />
        <StatCard
          label="Carbon Offset"
          value={buyerStats ? `${buyerStats.carbon_offset_kg} kg` : "—"}
          icon={<Leaf className="w-5 h-5" />}
          color="bg-emerald-50 text-emerald-600"
          trend={buyerStats ? `${buyerStats.active_requests} active requests` : undefined}
        />
      </div>

      <Card title="Recent Orders">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2 font-medium">Matched</th>
                <th className="pb-2 font-medium">Role</th>
                <th className="pb-2 font-medium">Quantity</th>
                <th className="pb-2 font-medium">Price</th>
                <th className="pb-2 font-medium">Status</th>
                <th className="pb-2 font-medium">Settled</th>
              </tr>
            </thead>
            <tbody>
              {(!orders || orders.length === 0) && (
                <tr><td colSpan={6} className="py-8 text-center text-gray-400">No orders yet</td></tr>
              )}
              {orders?.map((o) => (
                <tr key={o.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-3 text-gray-500">{new Date(o.matched_at).toLocaleDateString()}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      o.seller_id ? "bg-green-100 text-green-700" : "bg-blue-100 text-blue-700"
                    }`}>
                      {o.seller_id ? "Seller" : "Buyer"}
                    </span>
                  </td>
                  <td className="py-3">{(o.matched_wh / 1000).toFixed(1)} kWh</td>
                  <td className="py-3 font-mono">{o.price_cents_per_kwh}¢/kWh</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      o.status === "settled" ? "bg-green-100 text-green-700" :
                      o.status === "matched" ? "bg-yellow-100 text-yellow-700" :
                      o.status === "settling" ? "bg-blue-100 text-blue-700" :
                      "bg-gray-100 text-gray-600"
                    }`}>{o.status}</span>
                  </td>
                  <td className="py-3 text-gray-500 text-xs">{o.settled_at ? new Date(o.settled_at).toLocaleString() : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
