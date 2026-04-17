# =============================================================================
# models/__init__.py — Model Registry
# =============================================================================
# PURPOSE: Import ALL ORM models so they register with SQLAlchemy's metadata.
# This is CRITICAL for two reasons:
#
#   1. ALEMBIC MIGRATIONS: Alembic's autogenerate feature inspects
#      Base.metadata to detect tables. If a model isn't imported here,
#      Alembic won't see it and won't create its table.
#
#   2. RELATIONSHIP RESOLUTION: SQLAlchemy resolves string-based relationship
#      references (e.g., relationship("Zone")) by looking up registered models
#      in the metadata. All models must be imported for this to work.
#
# RULE: Every time you add a new model file, you MUST add an import here.
# =============================================================================

# Relational models (standard PostgreSQL tables)
from app.models.building import Building           # noqa: F401
from app.models.zone import Zone                   # noqa: F401
from app.models.user import User, UserRole         # noqa: F401
from app.models.forecast import Forecast           # noqa: F401
from app.models.recommendation import Recommendation  # noqa: F401

# Time-series models (TimescaleDB hypertables)
from app.models.sensor_reading import SensorReading   # noqa: F401
from app.models.hvac_status import HvacStatus         # noqa: F401
from app.models.energy_meter import EnergyMeter       # noqa: F401

# Phase 2 — Real-Time Intelligence
from app.models.alert_rule import AlertRule        # noqa: F401
from app.models.alert import Alert                 # noqa: F401
from app.models.notification import Notification   # noqa: F401
from app.models.notification_preference import NotificationPreference  # noqa: F401

# P2P Energy Trading models (Phase 9)
from app.models.p2p import (  # noqa: F401
    ProsumerProfile, ProsumerStatus,
    EnergyWallet,
    WalletLedger, LedgerEntryType,
    MeterReadingP2P,
    EnergyOffer, OfferStatus,
    EnergyRequest, RequestStatus,
    P2POrder, OrderStatus,
    P2PSettlement,
    TradingRule, RuleType,
    EnergyCommunity,
    CommunityMember, CommunityRole,
    P2PTaxSummary,
)
