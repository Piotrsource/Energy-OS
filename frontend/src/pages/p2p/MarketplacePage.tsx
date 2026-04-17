import { useState } from "react";
import { ShoppingCart, Tag, TrendingUp, TrendingDown, Zap, Clock } from "lucide-react";
import StatCard from "@/components/StatCard";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { EnergyOffer, EnergyRequest, MarketPrice, MarketStats } from "@/types";

function centsToPrice(cents: number) {
  return `${(cents / 100).toFixed(2)}`;
}

function whToKwh(wh: number) {
  return (wh / 1000).toFixed(1);
}

export default function MarketplacePage() {
  const { data: offers, loading: offersLoading, refetch: refetchOffers } = useApi<EnergyOffer[]>("/p2p/offers");
  const { data: requests, loading: requestsLoading, refetch: refetchRequests } = useApi<EnergyRequest[]>("/p2p/requests");
  const { data: price } = useApi<MarketPrice>("/p2p/market/price");
  const { data: stats } = useApi<MarketStats>("/p2p/market/stats");

  const [tab, setTab] = useState<"offers" | "requests">("offers");
  const [showForm, setShowForm] = useState(false);
  const [formType, setFormType] = useState<"sell" | "buy">("sell");
  const [formData, setFormData] = useState({
    quantity_kwh: "",
    price_cents: "",
    from: "",
    until: "",
  });
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const quantityWh = Math.round(parseFloat(formData.quantity_kwh) * 1000);
      const priceCents = parseInt(formData.price_cents);

      if (formType === "sell") {
        await api.post("/p2p/offers", {
          quantity_wh: quantityWh,
          price_cents_per_kwh: priceCents,
          available_from: new Date(formData.from).toISOString(),
          available_until: new Date(formData.until).toISOString(),
          min_purchase_wh: 0,
          auto_renew: false,
        });
        refetchOffers();
      } else {
        await api.post("/p2p/requests", {
          quantity_wh: quantityWh,
          max_price_cents_per_kwh: priceCents,
          preferred_from: new Date(formData.from).toISOString(),
          preferred_until: new Date(formData.until).toISOString(),
        });
        refetchRequests();
      }
      setShowForm(false);
      setFormData({ quantity_kwh: "", price_cents: "", from: "", until: "" });
    } catch {
      // handled by api client
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">P2P Energy Marketplace</h2>
          <p className="text-gray-500 text-sm mt-1">Buy and sell energy directly with your neighbors</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setFormType("sell"); setShowForm(true); }}
            className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition-colors"
          >
            + Sell Energy
          </button>
          <button
            onClick={() => { setFormType("buy"); setShowForm(true); }}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            + Buy Energy
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Suggested Sell Price"
          value={price ? `${price.suggested_sell_cents_per_kwh}¢/kWh` : "..."}
          icon={<TrendingUp className="w-5 h-5" />}
          color="bg-green-50 text-green-600"
        />
        <StatCard
          label="Suggested Buy Price"
          value={price ? `${price.suggested_buy_cents_per_kwh}¢/kWh` : "..."}
          icon={<TrendingDown className="w-5 h-5" />}
          color="bg-blue-50 text-blue-600"
        />
        <StatCard
          label="Trades (24h)"
          value={stats?.trades_last_24h ?? "..."}
          icon={<ShoppingCart className="w-5 h-5" />}
          color="bg-purple-50 text-purple-600"
        />
        <StatCard
          label="TOU Period"
          value={price?.time_of_use_period?.replace("_", " ") ?? "..."}
          icon={<Clock className="w-5 h-5" />}
          color="bg-yellow-50 text-yellow-600"
          trend={price ? `Grid: ${price.grid_retail_cents_per_kwh}¢ retail / ${price.grid_wholesale_cents_per_kwh}¢ wholesale` : undefined}
        />
      </div>

      {showForm && (
        <Card title={formType === "sell" ? "Create Sell Offer" : "Create Buy Request"}>
          <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Quantity (kWh)</label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                required
                value={formData.quantity_kwh}
                onChange={(e) => setFormData({ ...formData, quantity_kwh: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. 10"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {formType === "sell" ? "Ask Price (¢/kWh)" : "Max Price (¢/kWh)"}
              </label>
              <input
                type="number"
                min="1"
                required
                value={formData.price_cents}
                onChange={(e) => setFormData({ ...formData, price_cents: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder={formType === "sell"
                  ? `Suggested: ${price?.suggested_sell_cents_per_kwh ?? 15}`
                  : `Suggested: ${price?.suggested_buy_cents_per_kwh ?? 18}`}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Available From</label>
              <input
                type="datetime-local"
                required
                value={formData.from}
                onChange={(e) => setFormData({ ...formData, from: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Available Until</label>
              <input
                type="datetime-local"
                required
                value={formData.until}
                onChange={(e) => setFormData({ ...formData, until: e.target.value })}
                className="w-full border rounded-lg px-3 py-2 text-sm"
              />
            </div>
            <div className="md:col-span-2 flex gap-2 justify-end">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
                Cancel
              </button>
              <button
                type="submit"
                disabled={submitting}
                className={`px-4 py-2 text-sm text-white rounded-lg font-medium ${
                  formType === "sell" ? "bg-green-600 hover:bg-green-700" : "bg-blue-600 hover:bg-blue-700"
                } disabled:opacity-50`}
              >
                {submitting ? "Creating..." : formType === "sell" ? "Create Offer" : "Create Request"}
              </button>
            </div>
          </form>
        </Card>
      )}

      <Card>
        <div className="flex gap-4 mb-4 border-b pb-3">
          <button
            onClick={() => setTab("offers")}
            className={`text-sm font-medium pb-2 border-b-2 transition-colors ${
              tab === "offers" ? "border-green-600 text-green-600" : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <Tag className="w-4 h-4 inline mr-1" />
            Sell Offers ({offers?.length ?? 0})
          </button>
          <button
            onClick={() => setTab("requests")}
            className={`text-sm font-medium pb-2 border-b-2 transition-colors ${
              tab === "requests" ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            <ShoppingCart className="w-4 h-4 inline mr-1" />
            Buy Requests ({requests?.length ?? 0})
          </button>
        </div>

        {tab === "offers" && (
          offersLoading ? <Spinner /> : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2 font-medium">Price</th>
                    <th className="pb-2 font-medium">Quantity</th>
                    <th className="pb-2 font-medium">Remaining</th>
                    <th className="pb-2 font-medium">Window</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {offers?.length === 0 && (
                    <tr><td colSpan={5} className="py-8 text-center text-gray-400">No active offers</td></tr>
                  )}
                  {offers?.map((o) => (
                    <tr key={o.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-3 font-semibold text-green-700">{o.price_cents_per_kwh}¢/kWh</td>
                      <td className="py-3">{whToKwh(o.quantity_wh)} kWh</td>
                      <td className="py-3">{whToKwh(o.remaining_wh)} kWh</td>
                      <td className="py-3 text-xs text-gray-500">
                        {new Date(o.available_from).toLocaleDateString()} – {new Date(o.available_until).toLocaleDateString()}
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          o.status === "active" ? "bg-green-100 text-green-700" :
                          o.status === "partially_filled" ? "bg-yellow-100 text-yellow-700" :
                          "bg-gray-100 text-gray-600"
                        }`}>{o.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}

        {tab === "requests" && (
          requestsLoading ? <Spinner /> : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2 font-medium">Max Price</th>
                    <th className="pb-2 font-medium">Quantity</th>
                    <th className="pb-2 font-medium">Remaining</th>
                    <th className="pb-2 font-medium">Window</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {requests?.length === 0 && (
                    <tr><td colSpan={5} className="py-8 text-center text-gray-400">No active requests</td></tr>
                  )}
                  {requests?.map((r) => (
                    <tr key={r.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-3 font-semibold text-blue-700">{r.max_price_cents_per_kwh}¢/kWh</td>
                      <td className="py-3">{whToKwh(r.quantity_wh)} kWh</td>
                      <td className="py-3">{whToKwh(r.remaining_wh)} kWh</td>
                      <td className="py-3 text-xs text-gray-500">
                        {new Date(r.preferred_from).toLocaleDateString()} – {new Date(r.preferred_until).toLocaleDateString()}
                      </td>
                      <td className="py-3">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          r.status === "active" ? "bg-blue-100 text-blue-700" :
                          r.status === "partially_filled" ? "bg-yellow-100 text-yellow-700" :
                          "bg-gray-100 text-gray-600"
                        }`}>{r.status}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )
        )}
      </Card>
    </div>
  );
}
