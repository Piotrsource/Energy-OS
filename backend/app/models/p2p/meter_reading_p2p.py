import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MeterReadingP2P(Base):
    """
    Smart meter readings for P2P prosumers at 15-minute intervals.
    Stored as a TimescaleDB hypertable partitioned by time.
    All energy values in watt-hours (Wh) for integer precision.
    """
    __tablename__ = "meter_readings_p2p"
    __table_args__ = (
        PrimaryKeyConstraint("time", "meter_id"),
    )

    time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
    )
    meter_id: Mapped[str] = mapped_column(
        String(200), nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id"),
        nullable=False,
    )
    production_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    consumption_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    net_export_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    source: Mapped[str] = mapped_column(
        String(50), nullable=False, default="api",
    )
