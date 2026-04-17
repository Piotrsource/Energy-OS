import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class OrderStatus(str, enum.Enum):
    MATCHED = "matched"
    SETTLING = "settling"
    SETTLED = "settled"
    DISPUTED = "disputed"
    CANCELLED = "cancelled"


class P2POrder(Base):
    """
    A matched trade between a seller's offer and a buyer's request.
    Supports partial fills — matched_wh may be less than the full offer/request.
    """
    __tablename__ = "p2p_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    offer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("energy_offers.id"), nullable=False, index=True,
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("energy_requests.id"), nullable=False, index=True,
    )
    seller_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id"), nullable=False,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id"), nullable=False,
    )
    matched_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    price_cents_per_kwh: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=OrderStatus.MATCHED,
    )
    matched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )
    settled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    offer = relationship("EnergyOffer", back_populates="orders")
    request = relationship("EnergyRequest", back_populates="orders")
    settlements = relationship("P2PSettlement", back_populates="order")
