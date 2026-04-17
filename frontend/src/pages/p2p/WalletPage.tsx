import { useState } from "react";
import { Wallet, ArrowUpCircle, ArrowDownCircle, Clock, Zap } from "lucide-react";
import StatCard from "@/components/StatCard";
import Card from "@/components/Card";
import Spinner from "@/components/Spinner";
import { useApi } from "@/hooks/useApi";
import { api } from "@/api/client";
import type { EnergyWallet, LedgerEntry } from "@/types";

function formatCents(cents: number) {
  return `$${(cents / 100).toFixed(2)}`;
}

function formatWh(wh: number) {
  if (Math.abs(wh) >= 1000) return `${(wh / 1000).toFixed(1)} kWh`;
  return `${wh} Wh`;
}

const ENTRY_TYPE_LABELS: Record<string, { label: string; color: string }> = {
  energy_credit: { label: "Energy Credit", color: "text-green-600" },
  energy_debit: { label: "Energy Debit", color: "text-red-600" },
  cash_deposit: { label: "Deposit", color: "text-green-600" },
  cash_withdrawal: { label: "Withdrawal", color: "text-red-600" },
  sale_revenue: { label: "Sale Revenue", color: "text-green-600" },
  purchase_payment: { label: "Purchase", color: "text-red-600" },
  platform_fee: { label: "Platform Fee", color: "text-orange-600" },
  refund: { label: "Refund", color: "text-blue-600" },
};

export default function WalletPage() {
  const { data: wallet, loading: walletLoading, refetch: refetchWallet } = useApi<EnergyWallet>("/p2p/wallet");
  const { data: ledger, loading: ledgerLoading, refetch: refetchLedger } = useApi<LedgerEntry[]>("/p2p/wallet/ledger");

  const [action, setAction] = useState<"deposit" | "withdraw" | null>(null);
  const [amount, setAmount] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const cents = Math.round(parseFloat(amount) * 100);
      if (action === "deposit") {
        await api.post("/p2p/wallet/deposit", { amount_cents: cents });
      } else {
        await api.post("/p2p/wallet/withdraw", { amount_cents: cents });
      }
      refetchWallet();
      refetchLedger();
      setAction(null);
      setAmount("");
    } catch {
      // handled by api client
    } finally {
      setSubmitting(false);
    }
  };

  if (walletLoading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Energy Wallet</h2>
        <p className="text-gray-500 text-sm mt-1">Manage your energy credits and cash balance</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Cash Balance"
          value={wallet ? formatCents(wallet.cash_balance_cents) : "—"}
          icon={<Wallet className="w-5 h-5" />}
          color="bg-green-50 text-green-600"
        />
        <StatCard
          label="Energy Credits"
          value={wallet ? formatWh(wallet.energy_credits_wh) : "—"}
          icon={<Zap className="w-5 h-5" />}
          color="bg-yellow-50 text-yellow-600"
        />
        <StatCard
          label="Currency"
          value={wallet?.currency ?? "—"}
          icon={<Clock className="w-5 h-5" />}
          color="bg-blue-50 text-blue-600"
        />
        <StatCard
          label="Last Updated"
          value={wallet ? new Date(wallet.updated_at).toLocaleDateString() : "—"}
          icon={<Clock className="w-5 h-5" />}
        />
      </div>

      <div className="flex gap-2">
        <button
          onClick={() => setAction("deposit")}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
        >
          <ArrowDownCircle className="w-4 h-4" /> Deposit
        </button>
        <button
          onClick={() => setAction("withdraw")}
          className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700"
        >
          <ArrowUpCircle className="w-4 h-4" /> Withdraw
        </button>
      </div>

      {action && (
        <Card title={action === "deposit" ? "Deposit Funds" : "Withdraw Funds"}>
          <form onSubmit={handleSubmit} className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium text-gray-700 mb-1">Amount ($)</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full border rounded-lg px-3 py-2 text-sm"
                placeholder="e.g. 50.00"
              />
            </div>
            <button type="button" onClick={() => setAction(null)} className="px-4 py-2 text-sm text-gray-600">
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className={`px-4 py-2 text-sm text-white rounded-lg font-medium disabled:opacity-50 ${
                action === "deposit" ? "bg-green-600 hover:bg-green-700" : "bg-red-600 hover:bg-red-700"
              }`}
            >
              {submitting ? "Processing..." : action === "deposit" ? "Deposit" : "Withdraw"}
            </button>
          </form>
        </Card>
      )}

      <Card title="Transaction History">
        {ledgerLoading ? <Spinner /> : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 font-medium">Date</th>
                  <th className="pb-2 font-medium">Type</th>
                  <th className="pb-2 font-medium text-right">Amount</th>
                  <th className="pb-2 font-medium text-right">Energy</th>
                  <th className="pb-2 font-medium">Description</th>
                </tr>
              </thead>
              <tbody>
                {ledger?.length === 0 && (
                  <tr><td colSpan={5} className="py-8 text-center text-gray-400">No transactions yet</td></tr>
                )}
                {ledger?.map((entry) => {
                  const typeInfo = ENTRY_TYPE_LABELS[entry.entry_type] ?? { label: entry.entry_type, color: "text-gray-600" };
                  return (
                    <tr key={entry.id} className="border-b last:border-0 hover:bg-gray-50">
                      <td className="py-3 text-gray-500">{new Date(entry.created_at).toLocaleString()}</td>
                      <td className={`py-3 font-medium ${typeInfo.color}`}>{typeInfo.label}</td>
                      <td className={`py-3 text-right font-mono ${entry.amount_cents >= 0 ? "text-green-700" : "text-red-700"}`}>
                        {entry.amount_cents >= 0 ? "+" : ""}{formatCents(entry.amount_cents)}
                      </td>
                      <td className="py-3 text-right text-gray-500">
                        {entry.energy_wh !== 0 ? formatWh(entry.energy_wh) : "—"}
                      </td>
                      <td className="py-3 text-gray-500 text-xs max-w-[200px] truncate">{entry.description ?? "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
