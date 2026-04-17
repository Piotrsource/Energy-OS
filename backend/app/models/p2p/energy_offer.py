import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, String, Boolean, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OfferStatus(str, enum.Enum):
    ACTIVE = "active"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class EnergyOffer(Base):
    """
    A sell listing on the P2P marketplace.
    Seller specifies quantity (Wh), price (cents/kWh), and availability window.
    Supports partial fills — remaining_wh decrements as orders match.
    """
    __tablename__ = "energy_offers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_cents_per_kwh: Mapped[int] = mapped_column(Integer, nullable=False)
    available_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    available_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    min_purchase_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    remaining_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    auto_renew: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[OfferStatus] = mapped_column(
        Enum(OfferStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=OfferStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    seller = relationship("ProsumerProfile", backref="offers")
    orders = relationship("P2POrder", back_populates="offer")
