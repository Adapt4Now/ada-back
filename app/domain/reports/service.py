from typing import List

from sqlalchemy import select, func

from app.domain.tasks.models import Task
from app.domain.groups.associations import task_group_association
from app.domain.groups.membership import GroupMembership
from app.domain.tasks.schemas import TaskResponseSchema
from app.database import UnitOfWork


class ReportService:
    """Service layer for generating reports."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def get_task_summary(self) -> dict:
        async with self.uow as uow:
            total_result = await uow.session.execute(
                select(func.count()).select_from(Task).where(Task.deleted_at.is_(None))
            )
            total = total_result.scalar_one()
            completed_result = await uow.session.execute(
                select(func.count())
                .select_from(Task)
                .where(Task.is_completed.is_(True), Task.deleted_at.is_(None))
            )
            completed = completed_result.scalar_one()
        return {"total_tasks": total, "completed_tasks": completed}

    async def get_user_task_report(self, user_id: int) -> List[TaskResponseSchema]:
        async with self.uow as uow:
            result = await uow.session.execute(
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
        async with self.uow as uow:
            result = await uow.session.execute(stmt)
            tasks = result.scalars().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]

    async def get_group_task_report(self, group_id: int) -> List[TaskResponseSchema]:
        async with self.uow as uow:
            result = await uow.session.execute(
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
        async with self.uow as uow:
            result = await uow.session.execute(stmt)
            tasks = result.scalars().unique().all()
        return [TaskResponseSchema.model_validate(task) for task in tasks]
