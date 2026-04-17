import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RequestStatus(str, enum.Enum):
    ACTIVE = "active"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class EnergyRequest(Base):
    """
    A buy request on the P2P marketplace.
    Buyer specifies desired quantity, max price, and preferred time window.
    """
    __tablename__ = "energy_requests"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    buyer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    max_price_cents_per_kwh: Mapped[int] = mapped_column(Integer, nullable=False)
    preferred_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    preferred_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    remaining_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=RequestStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    buyer = relationship("ProsumerProfile", backref="requests")
    orders = relationship("P2POrder", back_populates="request")
