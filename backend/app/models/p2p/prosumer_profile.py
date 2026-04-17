import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProsumerStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DEACTIVATED = "deactivated"


class ProsumerProfile(Base):
    """
    Residential prosumer with solar/battery equipment.
    Links a platform user to their energy generation assets and smart meter.
    """
    __tablename__ = "prosumer_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)

    solar_capacity_kw: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    battery_capacity_kwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    inverter_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    meter_id: Mapped[str] = mapped_column(String(200), nullable=False)
    meter_provider: Mapped[str | None] = mapped_column(String(100), nullable=True)

    grid_agreement_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    status: Mapped[ProsumerStatus] = mapped_column(
        Enum(ProsumerStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=ProsumerStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    user = relationship("User", backref="prosumer_profile")
    wallet = relationship("EnergyWallet", back_populates="prosumer", uselist=False)
