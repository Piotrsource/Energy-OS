# =============================================================================
# services/user_service.py — User Business Logic
# =============================================================================
# PURPOSE: Encapsulate all database operations for users, including
# credential verification for the login flow.
#
# METHODS:
#   list_all()            → Get all users (admin only)
#   get_by_id()           → Get one user by UUID
#   get_by_email()        → Find user by email (for login)
#   create()              → Create a new user with hashed password
#   update()              → Partial update (including password change)
#   authenticate()        → Verify email + password for login
# =============================================================================

from uuid import UUID

from sqlalchemy import select, func as sa_func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.auth.passwords import hash_password, verify_password


class UserService:
    """Static methods for user management and authentication."""

    @staticmethod
    async def list_all(
        db: AsyncSession, *, offset: int = 0, limit: int = 50
    ) -> tuple[list[User], int]:
        count_result = await db.execute(select(sa_func.count()).select_from(User))
        total = count_result.scalar_one()

        result = await db.execute(
            select(User).order_by(User.name).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: UUID) -> User | None:
        """Retrieve a single user by UUID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        """
        Find a user by their email address.
        Used during login to look up the user before checking the password.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        """
        Create a new user. The plaintext password is hashed before storage.
        The role string is validated against the UserRole enum.
        """
        user = User(
            building_id=data.building_id,
            name=data.name,
            email=data.email,
            role=UserRole(data.role),
            password_hash=hash_password(data.password),
        )
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def update(
        db: AsyncSession, user_id: UUID, data: UserUpdate
    ) -> User | None:
        """
        Partially update a user. If a new password is provided, it is hashed.
        Returns the updated user, or None if not found.
        """
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None

        update_data = data.model_dump(exclude_unset=True)

        # Handle password change: hash the new password before storing
        if "password" in update_data:
            user.password_hash = hash_password(update_data.pop("password"))

        # Handle role change: convert string to enum
        if "role" in update_data:
            update_data["role"] = UserRole(update_data["role"])

        for field, value in update_data.items():
            setattr(user, field, value)

        await db.flush()
        return user

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
        """
        Verify a user's credentials for login.

        Args:
            email: The email the user provided.
            password: The plaintext password the user provided.

        Returns:
            The User object if credentials are valid, None otherwise.
        """
        user = await UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
