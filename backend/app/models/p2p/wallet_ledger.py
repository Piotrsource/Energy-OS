import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, ForeignKey, String, Enum, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LedgerEntryType(str, enum.Enum):
    ENERGY_CREDIT = "energy_credit"
    ENERGY_DEBIT = "energy_debit"
    CASH_DEPOSIT = "cash_deposit"
    CASH_WITHDRAWAL = "cash_withdrawal"
    SALE_REVENUE = "sale_revenue"
    PURCHASE_PAYMENT = "purchase_payment"
    PLATFORM_FEE = "platform_fee"
    REFUND = "refund"


class WalletLedger(Base):
    """
    Append-only double-entry ledger. Every trade creates a debit on the
    buyer's wallet and a credit on the seller's wallet.
    """
    __tablename__ = "wallet_ledger"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    wallet_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("energy_wallets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    amount_cents: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    energy_wh: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0,
    )
    counterparty_wallet_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("energy_wallets.id"), nullable=True,
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("p2p_orders.id"), nullable=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default="now()", nullable=False,
    )

    wallet = relationship("EnergyWallet", foreign_keys=[wallet_id], back_populates="ledger_entries")
