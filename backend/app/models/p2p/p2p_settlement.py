import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class P2PSettlement(Base):
    """
    Settlement record for a single 15-minute meter interval.
    Reconciles actual meter data against contracted trade quantities.
    All monetary values in integer cents.
    """
    __tablename__ = "p2p_settlements"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("p2p_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interval_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    interval_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    contracted_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    actual_delivered_wh: Mapped[int] = mapped_column(BigInteger, nullable=False)
    settlement_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    platform_fee_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    seller_credit_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    buyer_debit_cents: Mapped[int] = mapped_column(BigInteger, nullable=False)
    shortfall_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    order = relationship("P2POrder", back_populates="settlements")
