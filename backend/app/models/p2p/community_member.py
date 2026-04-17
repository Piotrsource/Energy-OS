import enum
import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CommunityRole(str, enum.Enum):
    ADMIN = "admin"
    MEMBER = "member"


class CommunityMember(Base):
    """Junction table linking prosumers to energy communities."""
    __tablename__ = "community_members"

    community_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("energy_communities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[CommunityRole] = mapped_column(
        Enum(CommunityRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        default=CommunityRole.MEMBER,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    community = relationship("EnergyCommunity", back_populates="members")
    prosumer = relationship("ProsumerProfile", backref="community_memberships")
