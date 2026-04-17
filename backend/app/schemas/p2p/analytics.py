from pydantic import BaseModel


class SellerAnalytics(BaseModel):
    total_kwh_sold: float
    total_revenue_cents: int
    avg_sell_price_cents_per_kwh: float
    production_vs_sold_ratio: float
    active_offers: int
    completed_orders: int
    earnings_projection_monthly_cents: int


class BuyerAnalytics(BaseModel):
    total_kwh_bought: float
    total_spent_cents: int
    avg_buy_price_cents_per_kwh: float
    savings_vs_grid_cents: int
    carbon_offset_kg: float
    active_requests: int
    completed_orders: int


class TaxSummaryRead(BaseModel):
    tax_year: int
    total_earnings_cents: int
    total_kwh_sold: int
    requires_1099: bool
