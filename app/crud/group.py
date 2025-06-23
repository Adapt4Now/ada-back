from typing import List, Optional, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate


async def create_group(db: AsyncSession, group: GroupCreate) -> Group:
    """Create a new group."""
    db_group = Group(**group.model_dump())
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group


async def get_group(
    db: AsyncSession,
    group_id: int,
    active_only: bool = True
) -> Optional[Group]:
    """Get a group by ID."""
    query = select(Group).where(Group.id == group_id)
    if active_only:
        query = query.where(Group.is_active.is_(True))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_groups(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True
) -> List[Group]:
    """Get a list of groups with pagination."""
    query = select(Group)
    if active_only:
        query = query.where(Group.is_active.is_(True))
    query = query.order_by(Group.id).offset(skip).limit(limit)
    result = await db.execute(query)
    groups = result.scalars().all()
    return cast(List[Group], list(groups))


async def update_group(
    db: AsyncSession,
    group_id: int,
    group_update: GroupUpdate
) -> Optional[Group]:
    """Update a group by ID."""
    db_group = await get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    update_data = group_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_group, field, value)

    await db.commit()
    await db.refresh(db_group)
    return db_group


async def delete_group(
    db: AsyncSession,
    group_id: int,
    hard_delete: bool = False
) -> Optional[Group]:
    """Delete a group by ID."""
    db_group = await get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    if hard_delete:
        await db.delete(db_group)
    else:
        db_group.is_active = False

    await db.commit()
    return db_group


async def get_groups_by_user(
    db: AsyncSession,
    user_id: int,
    active_only: bool = True
) -> List[Group]:
    """Get all groups that a user belongs to."""
    query = select(Group).where(Group.user_ids.contains([user_id]))
    if active_only:
        query = query.where(Group.is_active.is_(True))
    query = query.order_by(Group.id)
    result = await db.execute(query)
    groups = result.scalars().all()
    return cast(List[Group], list(groups))


async def add_users_to_group(
    db: AsyncSession,
    group_id: int,
    user_ids: List[int]
) -> Optional[Group]:
    """Add users to a group."""
    db_group = await get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    # Add new users without duplicates
    existing_users = set(db_group.user_ids)
    new_users = set(user_ids)
    db_group.user_ids = list(existing_users | new_users)

    await db.commit()
    await db.refresh(db_group)
    return db_group


async def remove_users_from_group(
    db: AsyncSession,
    group_id: int,
    user_ids: List[int]
) -> Optional[Group]:
    """Remove users from a group."""
    db_group = await get_group(db, group_id, active_only=False)
    if not db_group:
        return None

    # Remove specified users
    users_to_remove = set(user_ids)
    db_group.user_ids = [
        uid for uid in db_group.user_ids
        if uid not in users_to_remove
    ]

    await db.commit()
    await db.refresh(db_group)
    return db_group
