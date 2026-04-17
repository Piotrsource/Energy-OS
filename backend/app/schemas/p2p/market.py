from pydantic import BaseModel


class MarketPrice(BaseModel):
    suggested_sell_cents_per_kwh: int
    suggested_buy_cents_per_kwh: int
    grid_retail_cents_per_kwh: int
    grid_wholesale_cents_per_kwh: int
    supply_demand_ratio: float
    time_of_use_period: str


class MarketStats(BaseModel):
    active_offers: int
    active_requests: int
    total_available_wh: int
    total_requested_wh: int
    avg_offer_price_cents: float
    avg_request_price_cents: float
    trades_last_24h: int
    volume_last_24h_wh: int
