"""P2P Energy Trading — create all Phase 9 tables

Revision ID: 004_p2p_trading
Revises: 003_seed_admin
Create Date: 2026-03-02

PURPOSE:
    Creates 12 tables for the Peer-to-Peer Energy Trading module:

    RELATIONAL:
        - prosumer_profiles:  Residential prosumer registration & equipment
        - energy_wallets:     Dual-balance wallet (energy credits + cash)
        - wallet_ledger:      Append-only double-entry transaction log
        - energy_offers:      Sell listings on the marketplace
        - energy_requests:    Buy requests on the marketplace
        - p2p_orders:         Matched trades between offers and requests
        - p2p_settlements:    Per-interval settlement reconciliation
        - trading_rules:      User-configured automation rules (JSONB)
        - energy_communities: Groups of nearby prosumers
        - community_members:  Junction table for community membership
        - p2p_tax_summaries:  Annual tax reporting per seller

    TIME-SERIES (TimescaleDB hypertable):
        - meter_readings_p2p: Smart meter data at 15-min intervals
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_p2p_trading"
down_revision: Union[str, None] = "003_seed_admin"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================================================================
    # ENUM TYPES
    # =====================================================================
    prosumer_status = sa.Enum(
        "pending", "active", "suspended", "deactivated",
        name="prosumerstatus",
    )
    offer_status = sa.Enum(
        "active", "partially_filled", "filled", "expired", "cancelled",
        name="offerstatus",
    )
    request_status = sa.Enum(
        "active", "partially_filled", "filled", "expired", "cancelled",
        name="requeststatus",
    )
    order_status = sa.Enum(
        "matched", "settling", "settled", "disputed", "cancelled",
        name="orderstatus",
    )
    ledger_entry_type = sa.Enum(
        "energy_credit", "energy_debit",
        "cash_deposit", "cash_withdrawal",
        "sale_revenue", "purchase_payment",
        "platform_fee", "refund",
        name="ledgerentrytype",
    )
    rule_type = sa.Enum("auto_sell", "auto_buy", name="ruletype")
    community_role = sa.Enum("admin", "member", name="communityrole")

    # =====================================================================
    # PROSUMER PROFILES
    # =====================================================================
    op.create_table(
        "prosumer_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("solar_capacity_kw", sa.Float(), nullable=False, server_default="0"),
        sa.Column("battery_capacity_kwh", sa.Float(), nullable=False, server_default="0"),
        sa.Column("inverter_type", sa.String(100), nullable=True),
        sa.Column("meter_id", sa.String(200), nullable=False),
        sa.Column("meter_provider", sa.String(100), nullable=True),
        sa.Column("grid_agreement_accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", prosumer_status, nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
    )

    # =====================================================================
    # ENERGY WALLETS
    # =====================================================================
    op.create_table(
        "energy_wallets",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("energy_credits_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("cash_balance_cents", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
        sa.ForeignKeyConstraint(["user_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )

    # =====================================================================
    # ENERGY OFFERS (sell listings)
    # =====================================================================
    op.create_table(
        "energy_offers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_wh", sa.BigInteger(), nullable=False),
        sa.Column("price_cents_per_kwh", sa.Integer(), nullable=False),
        sa.Column("available_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("available_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("min_purchase_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("remaining_wh", sa.BigInteger(), nullable=False),
        sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("status", offer_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["seller_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_energy_offers_seller_id", "energy_offers", ["seller_id"])

    # =====================================================================
    # ENERGY REQUESTS (buy listings)
    # =====================================================================
    op.create_table(
        "energy_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("buyer_id", sa.Uuid(), nullable=False),
        sa.Column("quantity_wh", sa.BigInteger(), nullable=False),
        sa.Column("max_price_cents_per_kwh", sa.Integer(), nullable=False),
        sa.Column("preferred_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("preferred_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("remaining_wh", sa.BigInteger(), nullable=False),
        sa.Column("status", request_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["buyer_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_energy_requests_buyer_id", "energy_requests", ["buyer_id"])

    # =====================================================================
    # P2P ORDERS (matched trades)
    # =====================================================================
    op.create_table(
        "p2p_orders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("offer_id", sa.Uuid(), nullable=False),
        sa.Column("request_id", sa.Uuid(), nullable=False),
        sa.Column("seller_id", sa.Uuid(), nullable=False),
        sa.Column("buyer_id", sa.Uuid(), nullable=False),
        sa.Column("matched_wh", sa.BigInteger(), nullable=False),
        sa.Column("price_cents_per_kwh", sa.Integer(), nullable=False),
        sa.Column("status", order_status, nullable=False, server_default="matched"),
        sa.Column("matched_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("settled_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["offer_id"], ["energy_offers.id"]),
        sa.ForeignKeyConstraint(["request_id"], ["energy_requests.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["prosumer_profiles.id"]),
        sa.ForeignKeyConstraint(["buyer_id"], ["prosumer_profiles.id"]),
    )
    op.create_index("ix_p2p_orders_offer_id", "p2p_orders", ["offer_id"])
    op.create_index("ix_p2p_orders_request_id", "p2p_orders", ["request_id"])

    # =====================================================================
    # P2P SETTLEMENTS (per-interval reconciliation)
    # =====================================================================
    op.create_table(
        "p2p_settlements",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("order_id", sa.Uuid(), nullable=False),
        sa.Column("interval_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("contracted_wh", sa.BigInteger(), nullable=False),
        sa.Column("actual_delivered_wh", sa.BigInteger(), nullable=False),
        sa.Column("settlement_cents", sa.BigInteger(), nullable=False),
        sa.Column("platform_fee_cents", sa.BigInteger(), nullable=False),
        sa.Column("seller_credit_cents", sa.BigInteger(), nullable=False),
        sa.Column("buyer_debit_cents", sa.BigInteger(), nullable=False),
        sa.Column("shortfall_flag", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["order_id"], ["p2p_orders.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_p2p_settlements_order_id", "p2p_settlements", ["order_id"])

    # =====================================================================
    # WALLET LEDGER (append-only double-entry)
    # =====================================================================
    op.create_table(
        "wallet_ledger",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("wallet_id", sa.Uuid(), nullable=False),
        sa.Column("entry_type", ledger_entry_type, nullable=False),
        sa.Column("amount_cents", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("energy_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("counterparty_wallet_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["wallet_id"], ["energy_wallets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["counterparty_wallet_id"], ["energy_wallets.id"]),
        sa.ForeignKeyConstraint(["order_id"], ["p2p_orders.id"]),
    )
    op.create_index("ix_wallet_ledger_wallet_id", "wallet_ledger", ["wallet_id"])

    # =====================================================================
    # TRADING RULES (automated trading)
    # =====================================================================
    op.create_table(
        "trading_rules",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("rule_type", rule_type, nullable=False),
        sa.Column("conditions_json", postgresql.JSONB(), nullable=False),
        sa.Column("action_json", postgresql.JSONB(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_trading_rules_user_id", "trading_rules", ["user_id"])

    # =====================================================================
    # ENERGY COMMUNITIES
    # =====================================================================
    op.create_table(
        "energy_communities",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location_lat", sa.Float(), nullable=False),
        sa.Column("location_lng", sa.Float(), nullable=False),
        sa.Column("radius_km", sa.Float(), nullable=False, server_default="5"),
        sa.Column("fee_discount_pct", sa.Integer(), nullable=False, server_default="50"),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["created_by"], ["prosumer_profiles.id"]),
    )

    # =====================================================================
    # COMMUNITY MEMBERS (junction table)
    # =====================================================================
    op.create_table(
        "community_members",
        sa.Column("community_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", community_role, nullable=False, server_default="member"),
        sa.Column("joined_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("community_id", "user_id"),
        sa.ForeignKeyConstraint(["community_id"], ["energy_communities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )

    # =====================================================================
    # P2P TAX SUMMARIES
    # =====================================================================
    op.create_table(
        "p2p_tax_summaries",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("tax_year", sa.Integer(), nullable=False),
        sa.Column("total_earnings_cents", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("total_kwh_sold", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("report_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["prosumer_profiles.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_p2p_tax_summaries_user_id", "p2p_tax_summaries", ["user_id"])

    # =====================================================================
    # METER READINGS P2P (TimescaleDB hypertable)
    # =====================================================================
    op.create_table(
        "meter_readings_p2p",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("meter_id", sa.String(200), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("production_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("consumption_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("net_export_wh", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("source", sa.String(50), nullable=False, server_default="api"),
        sa.PrimaryKeyConstraint("time", "meter_id"),
        sa.ForeignKeyConstraint(["user_id"], ["prosumer_profiles.id"]),
    )

    # Convert to TimescaleDB hypertable
    op.execute(
        "SELECT create_hypertable('meter_readings_p2p', 'time', "
        "chunk_time_interval => INTERVAL '1 day', "
        "if_not_exists => TRUE);"
    )


def downgrade() -> None:
    op.drop_table("meter_readings_p2p")
    op.drop_table("p2p_tax_summaries")
    op.drop_table("community_members")
    op.drop_table("energy_communities")
    op.drop_table("trading_rules")
    op.drop_table("wallet_ledger")
    op.drop_table("p2p_settlements")
    op.drop_table("p2p_orders")
    op.drop_table("energy_requests")
    op.drop_table("energy_offers")
    op.drop_table("energy_wallets")
    op.drop_table("prosumer_profiles")

    # Drop enum types
    for name in [
        "prosumerstatus", "offerstatus", "requeststatus",
        "orderstatus", "ledgerentrytype", "ruletype", "communityrole",
    ]:
        sa.Enum(name=name).drop(op.get_bind())
