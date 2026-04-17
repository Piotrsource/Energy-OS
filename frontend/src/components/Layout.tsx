import { Link, useLocation, Outlet, Navigate } from "react-router-dom";
import { useAuth } from "@/context/AuthContext";
import ErrorBoundary from "@/components/ErrorBoundary";
import NotificationBell from "@/components/NotificationBell";
import {
  Building2,
  LayoutDashboard,
  Thermometer,
  BarChart3,
  Lightbulb,
  Activity,
  LogOut,
  Zap,
  ShoppingCart,
  Wallet,
  Users,
  TrendingUp,
  Bot,
  Bell,
  Radio,
  Settings,
} from "lucide-react";

const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/buildings", label: "Buildings", icon: Building2 },
  { path: "/sensors", label: "Sensors", icon: Thermometer },
  { path: "/hvac", label: "HVAC", icon: Activity },
  { path: "/forecasts", label: "Forecasts", icon: BarChart3 },
  { path: "/recommendations", label: "Recommendations", icon: Lightbulb },
  { path: "/analytics", label: "Analytics", icon: Zap },
  { path: "/alerts", label: "Alerts", icon: Bell },
  { path: "/device-health", label: "Device Health", icon: Radio },
];

const P2P_NAV_ITEMS = [
  { path: "/p2p/marketplace", label: "Marketplace", icon: ShoppingCart },
  { path: "/p2p/wallet", label: "Wallet", icon: Wallet },
  { path: "/p2p/communities", label: "Communities", icon: Users },
  { path: "/p2p/analytics", label: "Trading Stats", icon: TrendingUp },
  { path: "/p2p/rules", label: "Auto Rules", icon: Bot },
];

export default function Layout() {
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 bg-gray-900 text-white flex flex-col">
        <div className="p-5 border-b border-gray-700">
          <h1 className="text-lg font-bold flex items-center gap-2">
            <Zap className="w-5 h-5 text-yellow-400" />
            Energy Platform
          </h1>
          <p className="text-xs text-gray-400 mt-1">AI Optimization</p>
        </div>

        <nav className="flex-1 py-4 space-y-1 px-3 overflow-y-auto">
          {NAV_ITEMS.map(({ path, label, icon: Icon }) => {
            const active =
              path === "/"
                ? location.pathname === "/"
                : location.pathname.startsWith(path);
            return (
              <Link
                key={path}
                to={path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  active
                    ? "bg-primary-600 text-white"
                    : "text-gray-300 hover:bg-gray-800 hover:text-white"
                }`}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}

          <div className="pt-3 mt-3 border-t border-gray-700">
            <p className="px-3 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">P2P Trading</p>
            {P2P_NAV_ITEMS.map(({ path, label, icon: Icon }) => {
              const active = location.pathname.startsWith(path);
              return (
                <Link
                  key={path}
                  to={path}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    active
                      ? "bg-green-600 text-white"
                      : "text-gray-300 hover:bg-gray-800 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {label}
                </Link>
              );
            })}
          </div>
        </nav>

        <div className="p-3 border-t border-gray-700 space-y-1">
          <Link
            to="/settings/notifications"
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              location.pathname.startsWith("/settings")
                ? "bg-primary-600 text-white"
                : "text-gray-300 hover:bg-gray-800 hover:text-white"
            }`}
          >
            <Settings className="w-4 h-4" />
            Settings
          </Link>
          <button
            onClick={logout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white w-full transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-14 flex items-center justify-end px-6 border-b bg-white shrink-0">
          <NotificationBell />
        </header>
        <main className="flex-1 overflow-y-auto">
          <div className="p-6 max-w-7xl mx-auto">
            <ErrorBoundary>
              <Outlet />
            </ErrorBoundary>
          </div>
        </main>
      </div>
    </div>
  );
}
