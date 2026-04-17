import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EnergyWallet(Base):
    """
    Each prosumer gets one wallet with two balances:
    - energy_credits_wh: kWh available to sell (stored as Wh integer for precision)
    - cash_balance_cents: USD balance in integer cents
    """
    __tablename__ = "energy_wallets"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("prosumer_profiles.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    energy_credits_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    cash_balance_cents: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, default="USD",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", onupdate=datetime.utcnow, nullable=False,
    )

    prosumer = relationship("ProsumerProfile", back_populates="wallet")
    ledger_entries = relationship(
        "WalletLedger",
        back_populates="wallet",
        foreign_keys="[WalletLedger.wallet_id]",
        order_by="WalletLedger.created_at.desc()",
    )
