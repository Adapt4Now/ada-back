from typing import List
from datetime import datetime, UTC
from sqlalchemy import select, bindparam
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.base import BaseRepository
from .models import User, UserStatus
from .schemas import UserCreateSchema, UserUpdateSchema
from app.core.security import hash_password, generate_reset_token, verify_reset_token
from app.core.exceptions import UserNotFoundError


class UserRepository(BaseRepository[User]):
    """Repository for managing user operations."""

    model = User

    def __init__(self, db: AsyncSession):
        super().__init__(db)

    async def get_all(self) -> List[User]:
        """Retrieve all users."""
        return await self.get_list()

    async def create(self, user_data: UserCreateSchema) -> User:
        """Create a new user."""
        hashed_password = hash_password(user_data.password)
        data = user_data.model_dump()
        data["hashed_password"] = hashed_password
        data.pop("password", None)
        data.setdefault("status", UserStatus.ACTIVE)
        data.setdefault("created_at", datetime.now(UTC))
        data.setdefault("updated_at", datetime.now(UTC))
        return await super().create(data)

    async def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by id."""
        user = await self.get(user_id)
        if user is None:
            raise UserNotFoundError
        return user

    async def update(self, user_id: int, user_update: UserUpdateSchema) -> User:
        """Update an existing user."""
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        update_data["updated_at"] = datetime.now(UTC)
        user = await super().update(user_id, update_data)
        if user is None:
            raise UserNotFoundError
        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user by id."""
        user = await super().delete(user_id)
        if user is None:
            raise UserNotFoundError

    async def update_status(self, user_id: int, status: UserStatus) -> User:
        """Update only the status of a user."""
        user = await self.get_by_id(user_id)
        user.status = status
        user.updated_at = datetime.now(UTC)
        return user

    async def create_reset_token(self, email: str) -> str | None:
        """Create and store a password reset token for a user."""
        stmt = select(User).where(User.email == bindparam("e"))
        result = await self.db.execute(stmt, {"e": email})
        user = result.scalar_one_or_none()
        if user is None:
            return None
        token, expires_at = generate_reset_token()
        user.reset_token = token
        user.reset_token_expires_at = expires_at
        return token

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password using a valid reset token."""
        stmt = select(User).where(User.reset_token == bindparam("t"))
        result = await self.db.execute(stmt, {"t": token})
        user = result.scalar_one_or_none()
        if user is None or not verify_reset_token(user, token):
            return False
        user.hashed_password = hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires_at = None
        user.updated_at = datetime.now(UTC)
        return True

    async def get_by_username_or_email(
        self, username: str | None = None, email: str | None = None
    ) -> User | None:
        stmt = select(User)
        params: dict[str, str] = {}
        if username:
            stmt = stmt.where(User.username == bindparam("u"))
            params["u"] = username
        elif email:
            stmt = stmt.where(User.email == bindparam("e"))
            params["e"] = email
        result = await self.db.execute(stmt, params)
        return result.scalar_one_or_none()

    async def get_all_with_relations(self) -> List[User]:
        result = await self.db.execute(
            select(User).options(
                selectinload(User.family),
                selectinload(User.groups),
                selectinload(User.tasks),
                selectinload(User.notifications),
                selectinload(User.settings),
            )
        )
        return list(result.scalars().all())

    async def get_with_relations(self, user_id: int) -> User:
        stmt = (
            select(User)
            .where(User.id == bindparam("uid"))
            .options(
                selectinload(User.family),
                selectinload(User.groups),
                selectinload(User.tasks),
                selectinload(User.notifications),
                selectinload(User.settings),
            )
        )
        result = await self.db.execute(stmt, {"uid": user_id})
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError
        return user
