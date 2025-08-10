from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.task import Task, TaskStatus
from app.models.associations import task_group_association, user_group_membership
from app.schemas.task import TaskResponseSchema

router = APIRouter()


@router.get("/tasks/reports/summary")
async def get_task_summary(db: AsyncSession = Depends(get_database_session)):
    total_result = await db.execute(select(func.count()).select_from(Task))
    total = total_result.scalar_one()
    completed_result = await db.execute(
        select(func.count()).select_from(Task).where(Task.status == TaskStatus.COMPLETED)
    )
    completed = completed_result.scalar_one()
    return {"total_tasks": total, "completed_tasks": completed}


@router.get("/tasks/reports/user/{user_id}", response_model=List[TaskResponseSchema])
async def get_user_task_report(user_id: int, db: AsyncSession = Depends(get_database_session)):
    result = await db.execute(select(Task).where(Task.assigned_user_id == user_id))
    tasks = result.scalars().all()
    return [TaskResponseSchema.model_validate(task) for task in tasks]


@router.get("/tasks/reports/assigned-by/{user_id}", response_model=List[TaskResponseSchema])
async def get_tasks_assigned_by_user(
    user_id: int, db: AsyncSession = Depends(get_database_session)
):
    stmt = select(Task).where(
        Task.assigned_by_user_id == user_id,
        Task.assigned_user_id.isnot(None),
        Task.assigned_user_id != user_id,
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return [TaskResponseSchema.model_validate(task) for task in tasks]


@router.get("/tasks/reports/group/{group_id}", response_model=List[TaskResponseSchema])
async def get_group_task_report(group_id: int, db: AsyncSession = Depends(get_database_session)):
    result = await db.execute(
        select(Task).join(task_group_association).where(task_group_association.c.group_id == group_id)
    )
    tasks = result.scalars().all()
    return [TaskResponseSchema.model_validate(task) for task in tasks]


@router.get("/tasks/reports/user/{user_id}/groups", response_model=List[TaskResponseSchema])
async def get_user_groups_tasks(
    user_id: int, db: AsyncSession = Depends(get_database_session)
):
    stmt = (
        select(Task)
        .join(task_group_association)
        .join(
            user_group_membership,
            task_group_association.c.group_id == user_group_membership.c.group_id,
        )
        .where(user_group_membership.c.user_id == user_id)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().unique().all()
    return [TaskResponseSchema.model_validate(task) for task in tasks]
