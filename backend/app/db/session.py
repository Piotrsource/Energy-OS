# =============================================================================
# db/session.py — FastAPI Database Session Dependency
# =============================================================================
# PURPOSE: Provide a reusable FastAPI dependency that gives each request
# handler its own database session with automatic commit/rollback.
#
# HOW IT WORKS:
#   1. When a request arrives, FastAPI calls get_db() to create a new session.
#   2. The session is yielded to the route handler for executing queries.
#   3. After the handler returns successfully, the session is committed.
#   4. If an exception occurs, the session is rolled back instead.
#   5. Either way, the session is closed and its connection returns to the pool.
#
# USAGE IN ROUTE HANDLERS:
#   from fastapi import Depends
#   from sqlalchemy.ext.asyncio import AsyncSession
#   from app.db.session import get_db
#
#   @router.get("/buildings")
#   async def list_buildings(db: AsyncSession = Depends(get_db)):
#       result = await db.execute(select(Building))
#       return result.scalars().all()
#
# IMPORTANT:
#   Service methods should use db.flush() (not db.commit()) to get generated
#   IDs mid-request. The single commit happens here, at the end of the request.
# =============================================================================

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.

    The session follows a unit-of-work pattern:
    - All operations within a single request share one transaction.
    - Success → commit (all changes saved atomically).
    - Exception → rollback (no partial changes left in the database).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
