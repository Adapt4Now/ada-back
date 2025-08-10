from typing import List
from datetime import datetime, UTC
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserStatus
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import hash_password, generate_reset_token, verify_reset_token
from app.core.exceptions import UserNotFoundError


class UserRepository:
    """Repository for managing user operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> List[User]:
        """Retrieve all users."""
        result = await self.db.execute(select(User))
        return list(result.scalars().all())

    async def create(self, user_data: UserCreateSchema) -> User:
        """Create a new user."""
        hashed_password = hash_password(user_data.password)
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
            status=UserStatus.ACTIVE,
            is_superuser=user_data.is_superuser,
            is_premium=user_data.is_premium,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            avatar_url=user_data.avatar_url,
            locale=user_data.locale,
            timezone=user_data.timezone,
            points=user_data.points,
            level=user_data.level,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            created_by=user_data.created_by,
            family_id=user_data.family_id,
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by id."""
        stmt = select(User).where(User.id == bindparam("uid"))
        result = await self.db.execute(stmt, {"uid": user_id})
        user = result.scalar_one_or_none()
        if user is None:
            raise UserNotFoundError
        return user

    async def update(self, user_id: int, user_update: UserUpdateSchema) -> User:
        """Update an existing user."""
        user = await self.get_by_id(user_id)
        update_data = user_update.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = hash_password(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(user, field, value)
        user.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) -> None:
        """Delete a user by id."""
        user = await self.get_by_id(user_id)
        await self.db.delete(user)
        await self.db.commit()

    async def update_status(self, user_id: int, status: UserStatus) -> User:
        """Update only the status of a user."""
        user = await self.get_by_id(user_id)
        user.status = status
        user.updated_at = datetime.now(UTC)
        await self.db.commit()
        await self.db.refresh(user)
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
        await self.db.commit()
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
        await self.db.commit()
        return True
