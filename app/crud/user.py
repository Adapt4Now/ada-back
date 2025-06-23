from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, UTC
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.core.security import hash_password


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
        is_superuser=user_data.is_superuser,
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


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Retrieve a user by id."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdateSchema,
) -> Optional[User]:
    """Update an existing user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return None

    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(UTC)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete a user by id."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        return False
    await db.delete(user)
    await db.commit()
    return True
