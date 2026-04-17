import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import Layout from "@/components/Layout";
import ProtectedRoute from "@/components/ProtectedRoute";
import LoginPage from "@/pages/LoginPage";
import DashboardPage from "@/pages/DashboardPage";
import BuildingsPage from "@/pages/BuildingsPage";
import SensorsPage from "@/pages/SensorsPage";
import HvacPage from "@/pages/HvacPage";
import ForecastsPage from "@/pages/ForecastsPage";
import RecommendationsPage from "@/pages/RecommendationsPage";
import AnalyticsPage from "@/pages/AnalyticsPage";
import AlertsPage from "@/pages/AlertsPage";
import DeviceHealthPage from "@/pages/DeviceHealthPage";
import MarketplacePage from "@/pages/p2p/MarketplacePage";
import WalletPage from "@/pages/p2p/WalletPage";
import CommunitiesPage from "@/pages/p2p/CommunitiesPage";
import TradingAnalyticsPage from "@/pages/p2p/TradingAnalyticsPage";
import TradingRulesPage from "@/pages/p2p/TradingRulesPage";
import NotificationSettingsPage from "@/pages/NotificationSettingsPage";

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes — redirect to /login if unauthenticated */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/buildings" element={<BuildingsPage />} />
              <Route path="/sensors" element={<SensorsPage />} />
              <Route path="/hvac" element={<HvacPage />} />
              <Route path="/forecasts" element={<ForecastsPage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/device-health" element={<DeviceHealthPage />} />
              <Route path="/settings/notifications" element={<NotificationSettingsPage />} />
              <Route path="/p2p/marketplace" element={<MarketplacePage />} />
              <Route path="/p2p/wallet" element={<WalletPage />} />
              <Route path="/p2p/communities" element={<CommunitiesPage />} />
              <Route path="/p2p/analytics" element={<TradingAnalyticsPage />} />
              <Route path="/p2p/rules" element={<TradingRulesPage />} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
