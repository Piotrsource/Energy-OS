import { useEffect, useState } from "react";
import { api } from "@/api/client";
import type { NotificationPreference } from "@/types";
import { Bell, Mail, Shield, Moon, Save, Loader2, CheckCircle } from "lucide-react";

const SEVERITY_OPTIONS: NotificationPreference["min_severity"][] = [
  "low",
  "medium",
  "high",
  "critical",
];

const SEVERITY_LABELS: Record<string, string> = {
  low: "All notifications",
  medium: "Medium and above",
  high: "High and critical only",
  critical: "Critical only",
};

const HOUR_OPTIONS = Array.from({ length: 24 }, (_, i) => i);

function formatHour(h: number): string {
  const suffix = h >= 12 ? "PM" : "AM";
  const display = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${display}:00 ${suffix}`;
}

export default function NotificationSettingsPage() {
  const [prefs, setPrefs] = useState<NotificationPreference | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [inAppEnabled, setInAppEnabled] = useState(true);
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [minSeverity, setMinSeverity] = useState<NotificationPreference["min_severity"]>("low");
  const [emailAddress, setEmailAddress] = useState("");
  const [quietStart, setQuietStart] = useState<number | "">("");
  const [quietEnd, setQuietEnd] = useState<number | "">("");

  useEffect(() => {
    api
      .get<NotificationPreference>("/notifications/preferences")
      .then((p) => {
        setPrefs(p);
        setInAppEnabled(p.in_app_enabled);
        setEmailEnabled(p.email_enabled);
        setMinSeverity(p.min_severity);
        setEmailAddress(p.email_address || "");
        setQuietStart(p.quiet_start_hour ?? "");
        setQuietEnd(p.quiet_end_hour ?? "");
      })
      .catch(() => setError("Failed to load preferences"))
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setSaved(false);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        in_app_enabled: inAppEnabled,
        email_enabled: emailEnabled,
        min_severity: minSeverity,
        email_address: emailAddress || null,
        quiet_start_hour: quietStart === "" ? null : quietStart,
        quiet_end_hour: quietEnd === "" ? null : quietEnd,
      };
      const updated = await api.patch<NotificationPreference>("/notifications/preferences", body);
      setPrefs(updated);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError("Failed to save preferences");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 text-primary-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Notification Settings</h1>
        <p className="text-sm text-gray-500 mt-1">
          Configure how and when you receive alert notifications.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Channels */}
        <div className="bg-white rounded-xl border p-6 space-y-5">
          <div className="flex items-center gap-2 text-gray-800">
            <Bell className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold">Channels</h2>
          </div>

          <label className="flex items-center justify-between cursor-pointer group">
            <div className="flex items-center gap-3">
              <Bell className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-800">In-app notifications</p>
                <p className="text-xs text-gray-500">Show in the notification bell</p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={inAppEnabled}
              onChange={(e) => setInAppEnabled(e.target.checked)}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
          </label>

          <label className="flex items-center justify-between cursor-pointer group">
            <div className="flex items-center gap-3">
              <Mail className="w-4 h-4 text-gray-400" />
              <div>
                <p className="text-sm font-medium text-gray-800">Email notifications</p>
                <p className="text-xs text-gray-500">Send alerts to your email</p>
              </div>
            </div>
            <input
              type="checkbox"
              checked={emailEnabled}
              onChange={(e) => setEmailEnabled(e.target.checked)}
              className="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
          </label>

          {emailEnabled && (
            <div className="ml-7 pl-3 border-l-2 border-primary-100">
              <label className="block">
                <span className="text-xs font-medium text-gray-600">
                  Email address (leave blank to use account email)
                </span>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  placeholder="alerts@yourcompany.com"
                  className="mt-1 block w-full rounded-lg border-gray-300 shadow-sm text-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2 border"
                />
              </label>
            </div>
          )}
        </div>

        {/* Severity filter */}
        <div className="bg-white rounded-xl border p-6 space-y-5">
          <div className="flex items-center gap-2 text-gray-800">
            <Shield className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold">Severity Filter</h2>
          </div>
          <p className="text-sm text-gray-500">
            Only receive notifications at or above this severity level.
          </p>

          <div className="space-y-2">
            {SEVERITY_OPTIONS.map((sev) => (
              <label
                key={sev}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer border transition-colors ${
                  minSeverity === sev
                    ? "border-primary-300 bg-primary-50"
                    : "border-transparent hover:bg-gray-50"
                }`}
              >
                <input
                  type="radio"
                  name="severity"
                  value={sev}
                  checked={minSeverity === sev}
                  onChange={() => setMinSeverity(sev)}
                  className="text-primary-600 focus:ring-primary-500"
                />
                <div>
                  <p className="text-sm font-medium text-gray-800 capitalize">{sev}</p>
                  <p className="text-xs text-gray-500">{SEVERITY_LABELS[sev]}</p>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Quiet hours */}
        <div className="bg-white rounded-xl border p-6 space-y-5 md:col-span-2">
          <div className="flex items-center gap-2 text-gray-800">
            <Moon className="w-5 h-5 text-primary-500" />
            <h2 className="text-lg font-semibold">Quiet Hours</h2>
          </div>
          <p className="text-sm text-gray-500">
            Suppress non-critical notifications during these hours (UTC). Critical alerts always
            come through.
          </p>

          <div className="flex flex-wrap items-end gap-4">
            <label className="block">
              <span className="text-xs font-medium text-gray-600">Start</span>
              <select
                value={quietStart}
                onChange={(e) =>
                  setQuietStart(e.target.value === "" ? "" : Number(e.target.value))
                }
                className="mt-1 block w-40 rounded-lg border-gray-300 shadow-sm text-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2 border"
              >
                <option value="">Disabled</option>
                {HOUR_OPTIONS.map((h) => (
                  <option key={h} value={h}>
                    {formatHour(h)}
                  </option>
                ))}
              </select>
            </label>

            <label className="block">
              <span className="text-xs font-medium text-gray-600">End</span>
              <select
                value={quietEnd}
                onChange={(e) =>
                  setQuietEnd(e.target.value === "" ? "" : Number(e.target.value))
                }
                className="mt-1 block w-40 rounded-lg border-gray-300 shadow-sm text-sm focus:ring-primary-500 focus:border-primary-500 px-3 py-2 border"
              >
                <option value="">Disabled</option>
                {HOUR_OPTIONS.map((h) => (
                  <option key={h} value={h}>
                    {formatHour(h)}
                  </option>
                ))}
              </select>
            </label>

            {quietStart !== "" && quietEnd !== "" && (
              <p className="text-xs text-gray-500 pb-2">
                Notifications silenced from {formatHour(quietStart as number)} to{" "}
                {formatHour(quietEnd as number)} UTC
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Save button */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleSave}
          disabled={saving}
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          {saving ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Save className="w-4 h-4" />
          )}
          {saving ? "Saving..." : "Save Preferences"}
        </button>

        {saved && (
          <span className="inline-flex items-center gap-1 text-sm text-green-600">
            <CheckCircle className="w-4 h-4" />
            Saved successfully
          </span>
        )}
      </div>
    </div>
  );
}
