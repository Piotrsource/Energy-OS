import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class P2PTaxSummary(Base):
    """
    Annual tax summary per prosumer.
    In the US, sellers earning > $600/year need 1099 reporting.
    """
    __tablename__ = "p2p_tax_summaries"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tax_year: Mapped[int] = mapped_column(Integer, nullable=False)
    total_earnings_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    total_kwh_sold: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    report_generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    prosumer = relationship("ProsumerProfile", backref="tax_summaries")
