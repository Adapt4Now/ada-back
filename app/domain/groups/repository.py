from typing import List, Optional, cast

from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.groups.membership import GroupMembership
from app.domain.base import BaseRepository

from .models import Group
from .schemas import GroupCreate, GroupUpdate


class GroupRepository(BaseRepository[Group]):
    """Repository for managing groups."""

    model = Group

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def create(self, group: GroupCreate) -> Group:
        return await super().create(group.model_dump())

    async def get(self, group_id: int, active_only: bool = True) -> Optional[Group]:
        query = select(self.model).where(self.model.id == group_id)
        if active_only:
            query = query.where(self.model.is_active.is_(True))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_list(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[Group]:
        query = select(self.model)
        if active_only:
            query = query.where(self.model.is_active.is_(True))
        query = query.order_by(self.model.id).offset(skip).limit(limit)
        result = await self.session.execute(query)
        groups = result.scalars().all()
        return cast(List[Group], list(groups))

    async def update(self, group_id: int, group_update: GroupUpdate) -> Optional[Group]:
        return await super().update(group_id, group_update.model_dump(exclude_unset=True))

    async def delete(
        self, group_id: int, hard_delete: bool = False
    ) -> Optional[Group]:
        if hard_delete:
            return await super().delete(group_id)
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        db_group.is_active = False
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
        result = await self.session.execute(query)
        groups = result.scalars().all()
        return cast(List[Group], list(groups))

    async def add_users(
        self, group_id: int, user_roles: dict[int, str]
    ) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        for uid, role in user_roles.items():
            await self.session.execute(
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
        return db_group

    async def remove_users(
        self, group_id: int, user_ids: List[int]
    ) -> Optional[Group]:
        db_group = await self.get(group_id, active_only=False)
        if not db_group:
            return None
        await self.session.execute(
            delete(GroupMembership).where(
                GroupMembership.group_id == group_id,
                GroupMembership.user_id.in_(user_ids),
            )
        )
        return db_group
