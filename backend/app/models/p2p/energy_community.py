import uuid
from datetime import datetime

from sqlalchemy import Float, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EnergyCommunity(Base):
    """
    A group of nearby prosumers who trade preferentially.
    Members get lower fees and priority matching within the community.
    """
    __tablename__ = "energy_communities"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_lat: Mapped[float] = mapped_column(Float, nullable=False)
    location_lng: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, nullable=False, default=5.0)
    fee_discount_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    members = relationship("CommunityMember", back_populates="community", cascade="all, delete-orphan")
    creator = relationship("ProsumerProfile", backref="created_communities")
