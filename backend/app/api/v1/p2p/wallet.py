from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.wallet import WalletRead, WalletDeposit, WalletWithdraw, LedgerEntryRead
from app.services.p2p.prosumer_service import ProsumerService
from app.services.p2p.wallet_service import WalletService

router = APIRouter()


async def _get_prosumer_id(db, user):
    profile = await ProsumerService.get_by_user_id(db, user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return profile.id


@router.get(
    "/",
    response_model=WalletRead,
    summary="Get wallet balance",
)
async def get_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = await _get_prosumer_id(db, current_user)
    wallet = await WalletService.get_by_prosumer_id(db, pid)
    if not wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")
    return wallet


@router.post(
    "/deposit",
    response_model=WalletRead,
    summary="Deposit funds into wallet",
)
async def deposit(
    payload: WalletDeposit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = await _get_prosumer_id(db, current_user)
    try:
        return await WalletService.deposit(db, pid, payload.amount_cents)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.post(
    "/withdraw",
    response_model=WalletRead,
    summary="Withdraw funds from wallet",
)
async def withdraw(
    payload: WalletWithdraw,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = await _get_prosumer_id(db, current_user)
    try:
        return await WalletService.withdraw(db, pid, payload.amount_cents)
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))


@router.get(
    "/ledger",
    response_model=list[LedgerEntryRead],
    summary="Transaction history",
)
async def get_ledger(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pid = await _get_prosumer_id(db, current_user)
    wallet = await WalletService.get_by_prosumer_id(db, pid)
    if not wallet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Wallet not found")
    return await WalletService.get_ledger(db, wallet.id, limit, offset)
