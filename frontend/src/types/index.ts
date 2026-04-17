export interface PaginatedResponse<T> {
  items: T[];
  total_count: number;
  offset: number;
  limit: number;
}

export interface Building {
  id: string;
  name: string;
  address: string;
  type: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface Zone {
  id: string;
  building_id: string;
  name: string;
  floor: number | null;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  building_id: string;
  name: string;
  email: string;
  role: "admin" | "facility_manager" | "technician";
  created_at: string;
  updated_at: string;
}

export interface SensorReading {
  time: string;
  sensor_id: string;
  building_id: string;
  zone_id: string;
  sensor_type: string;
  value: number;
}

export interface HvacStatus {
  time: string;
  device_id: string;
  building_id: string;
  zone_id: string;
  device_type: string;
  status: string;
  setpoint: number | null;
}

export interface Forecast {
  id: string;
  zone_id: string;
  forecast_type: string;
  predicted_value: number;
  forecast_time: string;
  created_at: string;
}

export interface Recommendation {
  id: string;
  zone_id: string;
  recommendation_type: string;
  value: number;
  status: "pending" | "approved" | "applied" | "rejected";
  created_at: string;
  applied_at: string | null;
}

export interface EnergyBucket {
  bucket: string;
  total_kwh: number;
  avg_kwh: number;
  peak_kwh: number;
}

export interface EnergySummary {
  building_id: string;
  start: string;
  end: string;
  buckets: EnergyBucket[];
  total_kwh: number;
}

export interface CarbonBucket {
  bucket: string;
  total_kwh: number;
  carbon_kg: number;
}

export interface CarbonEmissions {
  building_id: string;
  start: string;
  end: string;
  emission_factor_kg_per_kwh: number;
  buckets: CarbonBucket[];
  total_carbon_kg: number;
}

export interface AnomalyRecord {
  id: string;
  building_id: string;
  zone_id: string | null;
  timestamp: string;
  sensor_type: string;
  expected_value: number;
  actual_value: number;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// =========================================================================
// P2P Energy Trading Types
// =========================================================================

export interface ProsumerProfile {
  id: string;
  user_id: string;
  address: string;
  lat: number;
  lng: number;
  solar_capacity_kw: number;
  battery_capacity_kwh: number;
  inverter_type: string | null;
  meter_id: string;
  meter_provider: string | null;
  grid_agreement_accepted_at: string | null;
  status: "pending" | "active" | "suspended" | "deactivated";
  created_at: string;
}

export interface EnergyWallet {
  id: string;
  user_id: string;
  energy_credits_wh: number;
  cash_balance_cents: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

export interface LedgerEntry {
  id: string;
  wallet_id: string;
  entry_type: string;
  amount_cents: number;
  energy_wh: number;
  counterparty_wallet_id: string | null;
  order_id: string | null;
  description: string | null;
  created_at: string;
}

export interface EnergyOffer {
  id: string;
  seller_id: string;
  quantity_wh: number;
  price_cents_per_kwh: number;
  available_from: string;
  available_until: string;
  min_purchase_wh: number;
  remaining_wh: number;
  auto_renew: boolean;
  status: string;
  created_at: string;
}

export interface EnergyRequest {
  id: string;
  buyer_id: string;
  quantity_wh: number;
  max_price_cents_per_kwh: number;
  preferred_from: string;
  preferred_until: string;
  remaining_wh: number;
  status: string;
  created_at: string;
}

export interface P2POrder {
  id: string;
  offer_id: string;
  request_id: string;
  seller_id: string;
  buyer_id: string;
  matched_wh: number;
  price_cents_per_kwh: number;
  status: string;
  matched_at: string;
  settled_at: string | null;
}

export interface MarketPrice {
  suggested_sell_cents_per_kwh: number;
  suggested_buy_cents_per_kwh: number;
  grid_retail_cents_per_kwh: number;
  grid_wholesale_cents_per_kwh: number;
  supply_demand_ratio: number;
  time_of_use_period: string;
}

export interface MarketStats {
  active_offers: number;
  active_requests: number;
  total_available_wh: number;
  total_requested_wh: number;
  avg_offer_price_cents: number;
  avg_request_price_cents: number;
  trades_last_24h: number;
  volume_last_24h_wh: number;
}

export interface SellerAnalytics {
  total_kwh_sold: number;
  total_revenue_cents: number;
  avg_sell_price_cents_per_kwh: number;
  production_vs_sold_ratio: number;
  active_offers: number;
  completed_orders: number;
  earnings_projection_monthly_cents: number;
}

export interface BuyerAnalytics {
  total_kwh_bought: number;
  total_spent_cents: number;
  avg_buy_price_cents_per_kwh: number;
  savings_vs_grid_cents: number;
  carbon_offset_kg: number;
  active_requests: number;
  completed_orders: number;
}

export interface TradingRule {
  id: string;
  user_id: string;
  rule_type: "auto_sell" | "auto_buy";
  conditions_json: Record<string, unknown>;
  action_json: Record<string, unknown>;
  enabled: boolean;
  description: string | null;
  last_triggered_at: string | null;
  created_at: string;
}

export interface EnergyCommunity {
  id: string;
  name: string;
  description: string | null;
  location_lat: number;
  location_lng: number;
  radius_km: number;
  fee_discount_pct: number;
  created_by: string;
  created_at: string;
  member_count: number;
}

export interface CommunityDashboard {
  community_id: string;
  community_name: string;
  member_count: number;
  total_trades: number;
  total_kwh_traded: number;
  total_value_cents: number;
  avg_price_cents_per_kwh: number;
  grid_independence_pct: number;
  co2_avoided_kg: number;
}

// =========================================================================
// Phase 2 — Real-Time Intelligence Types
// =========================================================================

export interface AlertRule {
  id: string;
  building_id: string;
  zone_id: string | null;
  sensor_type: string;
  condition: "gt" | "lt" | "eq" | "gte" | "lte";
  threshold: number;
  severity: "low" | "medium" | "high" | "critical";
  enabled: boolean;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  triggered_at: string;
  sensor_id: string;
  value: number;
  acknowledged_at: string | null;
  acknowledged_by: string | null;
}

export interface Notification {
  id: string;
  user_id: string;
  alert_id: string | null;
  channel: string;
  title: string;
  body: string;
  sent_at: string;
  read_at: string | null;
}

export interface DeviceHealth {
  sensor_id: string;
  building_id: string;
  zone_id: string;
  sensor_type: string;
  last_seen: string;
  last_value: number;
  status: "online" | "stale" | "offline";
}

export interface NotificationPreference {
  id: string;
  user_id: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  min_severity: "low" | "medium" | "high" | "critical";
  email_address: string | null;
  quiet_start_hour: number | null;
  quiet_end_hour: number | null;
  created_at: string;
  updated_at: string;
}
