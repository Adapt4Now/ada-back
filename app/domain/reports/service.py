from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.tasks.models import Task
from app.domain.groups.associations import task_group_association
from app.domain.groups.membership import GroupMembership
from app.domain.tasks.schemas import TaskResponseSchema


class ReportService:
    """Service layer for generating reports."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_task_summary(self) -> dict:
        total_result = await self.db.execute(
            select(func.count()).select_from(Task).where(Task.deleted_at.is_(None))
        )
        total = total_result.scalar_one()
        completed_result = await self.db.execute(
            select(func.count())
            .select_from(Task)
            .where(Task.is_completed.is_(True), Task.deleted_at.is_(None))
        )
        completed = completed_result.scalar_one()
        return {"total_tasks": total, "completed_tasks": completed}

    async def get_user_task_report(self, user_id: int) -> List[TaskResponseSchema]:
        result = await self.db.execute(
            select(Task).where(Task.assigned_user_id == user_id, Task.deleted_at.is_(None))
        )
        tasks = result.scalars().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]

    async def get_tasks_assigned_by_user(self, user_id: int) -> List[TaskResponseSchema]:
        stmt = select(Task).where(
            Task.assigned_by_user_id == user_id,
            Task.assigned_user_id.isnot(None),
            Task.assigned_user_id != user_id,
            Task.deleted_at.is_(None),
        )
        result = await self.db.execute(stmt)
        tasks = result.scalars().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]

    async def get_group_task_report(self, group_id: int) -> List[TaskResponseSchema]:
        result = await self.db.execute(
            select(Task)
            .join(task_group_association)
            .where(
                task_group_association.c.group_id == group_id,
                Task.deleted_at.is_(None),
            )
        )
        tasks = result.scalars().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]

    async def get_user_groups_tasks(self, user_id: int) -> List[TaskResponseSchema]:
        stmt = (
            select(Task)
            .join(task_group_association)
            .join(
                GroupMembership,
                task_group_association.c.group_id == GroupMembership.group_id,
            )
            .where(GroupMembership.user_id == user_id)
        )
        result = await self.db.execute(stmt)
        tasks = result.scalars().unique().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]
