from typing import List
from pydantic import BaseModel
from datetime import datetime, UTC
from sqlalchemy import select, bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserStatus
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import (
    generate_reset_token,
    hash_password,
    verify_reset_token,
)
from app.core.exceptions import UserNotFoundError


class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True


async def get_users(db: AsyncSession) -> List[User]:
    """Retrieve all users from the database."""
    result = await db.execute(select(User))
    return list(result.scalars().all())




async def create_user(db: AsyncSession, user_data: UserCreateSchema) -> User:
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
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user(db: AsyncSession, user_id: int) -> User:
    """Retrieve a user by id."""
    stmt = select(User).where(User.id == bindparam("uid"))
    result = await db.execute(stmt, {"uid": user_id})
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")
    return user


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdateSchema,
) -> User:
    """Update an existing user."""
    stmt = select(User).where(User.id == bindparam("uid"))
    result = await db.execute(stmt, {"uid": user_id})
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    """Delete a user by id."""
    stmt = select(User).where(User.id == bindparam("uid"))
    result = await db.execute(stmt, {"uid": user_id})
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")
    await db.delete(user)
    await db.commit()


async def update_user_status(
    db: AsyncSession, user_id: int, status: UserStatus
) -> User:
    """Update only the status of a user."""
    stmt = select(User).where(User.id == bindparam("uid"))
    result = await db.execute(stmt, {"uid": user_id})
    user = result.scalar_one_or_none()
    if user is None:
        raise UserNotFoundError(f"User with id {user_id} not found")
    user.status = status
    user.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(user)
    return user
