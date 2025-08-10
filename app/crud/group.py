from typing import List, Optional, cast

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.group import Group
from app.models.membership import GroupMembership
from app.schemas.group import GroupCreate, GroupUpdate


class GroupRepository:
    """Repository for managing groups."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, group: GroupCreate) -> Group:
        db_group = Group(**group.model_dump())
        self.db.add(db_group)
        await self.db.commit()
        await self.db.refresh(db_group)
        return db_group

    async def get(self, group_id: int, active_only: bool = True) -> Optional[Group]:
        query = select(Group).where(Group.id == group_id)
        if active_only:
            query = query.where(Group.is_active.is_(True))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_list(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Group]:
        query = select(Group)
        if active_only:
            query = query.where(Group.is_active.is_(True))
        query = query.order_by(Group.id).offset(skip).limit(limit)
        result = await self.db.execute(query)
        groups = result.scalars().all()
        return cast(List[Group], list(groups))

    async def update(self, group_id: int, group_update: GroupUpdate) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        update_data = group_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_group, field, value)
        await self.db.commit()
        await self.db.refresh(db_group)
        return db_group

    async def delete(
        self, group_id: int, hard_delete: bool = False
    ) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        if hard_delete:
            await self.db.delete(db_group)
        else:
            db_group.is_active = False
        await self.db.commit()
        return db_group

    async def get_by_user(
        self, user_id: int, active_only: bool = True
    ) -> List[Group]:
        query = (
            select(Group)
            .join(GroupMembership, Group.id == GroupMembership.group_id)
            .where(GroupMembership.user_id == user_id)
        )
        if active_only:
            query = query.where(Group.is_active.is_(True))
        query = query.order_by(Group.id)
        result = await self.db.execute(query)
        groups = result.scalars().all()
        return cast(List[Group], list(groups))

    async def add_users(
        self, group_id: int, user_roles: dict[int, str]
    ) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        for uid, role in user_roles.items():
            await self.db.execute(
                insert(GroupMembership)
                .values(user_id=uid, group_id=group_id, role=role)
                .on_conflict_do_update(
                    index_elements=[
                        GroupMembership.user_id,
                        GroupMembership.group_id,
                    ],
                    set_={"role": role},
                )
            )
        await self.db.commit()
        await self.db.refresh(db_group)
        return db_group

    async def remove_users(
        self, group_id: int, user_ids: List[int]
    ) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        await self.db.execute(
            delete(GroupMembership).where(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id.in_(user_ids),
            )
        )
        await self.db.commit()
        await self.db.refresh(db_group)
        return db_group
