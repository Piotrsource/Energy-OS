from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.p2p.energy_wallet import EnergyWallet
from app.models.p2p.wallet_ledger import WalletLedger, LedgerEntryType


class WalletService:

    @staticmethod
    async def get_by_prosumer_id(db: AsyncSession, prosumer_id: UUID) -> EnergyWallet | None:
        result = await db.execute(
            select(EnergyWallet).where(EnergyWallet.user_id == prosumer_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def deposit(db: AsyncSession, prosumer_id: UUID, amount_cents: int) -> EnergyWallet:
        wallet = await WalletService.get_by_prosumer_id(db, prosumer_id)
        if not wallet:
            raise ValueError("Wallet not found")

        wallet.cash_balance_cents += amount_cents
        wallet.updated_at = datetime.now(timezone.utc)

        entry = WalletLedger(
            wallet_id=wallet.id,
            entry_type=LedgerEntryType.CASH_DEPOSIT,
            amount_cents=amount_cents,
            description=f"Deposit of {amount_cents} cents",
        )
        db.add(entry)
        await db.flush()
        return wallet

    @staticmethod
    async def withdraw(db: AsyncSession, prosumer_id: UUID, amount_cents: int) -> EnergyWallet:
        wallet = await WalletService.get_by_prosumer_id(db, prosumer_id)
        if not wallet:
            raise ValueError("Wallet not found")
        if wallet.cash_balance_cents < amount_cents:
            raise ValueError("Insufficient balance")

        wallet.cash_balance_cents -= amount_cents
        wallet.updated_at = datetime.now(timezone.utc)

        entry = WalletLedger(
            wallet_id=wallet.id,
            entry_type=LedgerEntryType.CASH_WITHDRAWAL,
            amount_cents=-amount_cents,
            description=f"Withdrawal of {amount_cents} cents",
        )
        db.add(entry)
        await db.flush()
        return wallet

    @staticmethod
    async def get_ledger(
        db: AsyncSession, wallet_id: UUID, limit: int = 50, offset: int = 0,
    ) -> list[WalletLedger]:
        result = await db.execute(
            select(WalletLedger)
            .where(WalletLedger.wallet_id == wallet_id)
            .order_by(WalletLedger.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    @staticmethod
    async def credit_sale(
        db: AsyncSession,
        seller_wallet: EnergyWallet,
        buyer_wallet: EnergyWallet,
        amount_cents: int,
        energy_wh: int,
        platform_fee_cents: int,
        order_id: UUID,
    ) -> None:
        """Execute the double-entry bookkeeping for a settled trade."""
        net_seller_cents = amount_cents - platform_fee_cents

        seller_wallet.cash_balance_cents += net_seller_cents
        seller_wallet.energy_credits_wh = max(0, seller_wallet.energy_credits_wh - energy_wh)
        seller_wallet.updated_at = datetime.now(timezone.utc)

        buyer_wallet.cash_balance_cents -= amount_cents
        buyer_wallet.energy_credits_wh += energy_wh
        buyer_wallet.updated_at = datetime.now(timezone.utc)

        db.add(WalletLedger(
            wallet_id=seller_wallet.id,
            entry_type=LedgerEntryType.SALE_REVENUE,
            amount_cents=net_seller_cents,
            energy_wh=-energy_wh,
            counterparty_wallet_id=buyer_wallet.id,
            order_id=order_id,
            description=f"Sale: {energy_wh}Wh at {amount_cents}c (fee: {platform_fee_cents}c)",
        ))
        db.add(WalletLedger(
            wallet_id=seller_wallet.id,
            entry_type=LedgerEntryType.PLATFORM_FEE,
            amount_cents=-platform_fee_cents,
            order_id=order_id,
            description=f"Platform fee: {platform_fee_cents}c",
        ))
        db.add(WalletLedger(
            wallet_id=buyer_wallet.id,
            entry_type=LedgerEntryType.PURCHASE_PAYMENT,
            amount_cents=-amount_cents,
            energy_wh=energy_wh,
            counterparty_wallet_id=seller_wallet.id,
            order_id=order_id,
            description=f"Purchase: {energy_wh}Wh at {amount_cents}c",
        ))
        await db.flush()
