from typing import List
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserCreate(BaseModel):
    """Schema for user creation."""
    username: str
    email: str
    password: str

    class Config:
        from_attributes = True


async def get_users(db: AsyncSession) -> List[dict]:
    """
    Retrieve all users from the database.

    Args:
        db: Database session

    Returns:
        List of users as dictionaries
    """
    async with db as session:
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()
        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                # Преобразуем SQLAlchemy Boolean в Python bool
                "is_active": bool(user.is_active) if user.is_active is not None else True
            }
            for user in users
        ]
