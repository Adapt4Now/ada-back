
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.task import Task
from app.schemas.task import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get(
    "/",
    response_model=List[TaskResponseSchema],
    summary="Get all tasks"
)
async def get_tasks(
        db: AsyncSession = Depends(get_database_session)
) -> List[TaskResponseSchema]:
    """
    Retrieve all tasks from the system.
    """
    query = select(Task)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return [TaskResponseSchema.model_validate(task) for task in tasks]


@router.post(
    "/",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task"
)
async def create_task(
        task_data: TaskCreateSchema,
        db: AsyncSession = Depends(get_database_session)
) -> TaskResponseSchema:
    """
    Create a new task with the provided data.
    """
    new_task = Task(**task_data.model_dump())
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return TaskResponseSchema.model_validate(new_task)


@router.get(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Get task by ID"
)
async def get_task_by_id(
        task_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> TaskResponseSchema:
    """
    Get detailed information about a specific task.
    """
    query = select(Task).where(Task.id.is_(task_id))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponseSchema.model_validate(task)


@router.put(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Update task"
)
async def update_task(
        task_id: int,
        task_data: TaskUpdateSchema,
        db: AsyncSession = Depends(get_database_session)
) -> TaskResponseSchema:
    """
    Update task information.
    """
    query = select(Task).where(Task.id.is_(task_id))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    for field, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return TaskResponseSchema.model_validate(task)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task"
)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> None:
    """
    Delete a task from the system.
    """
    query = select(Task).where(Task.id.is_(task_id))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    await db.delete(task)
    await db.commit()


@router.post(
    "/{task_id}/assign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Assign task to user"
)
async def assign_task_to_user(
        task_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> TaskResponseSchema:
    """
    Assign a task to a specific user.
    """
    query = select(Task).where(Task.id.is_(task_id))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.assigned_user_id = user_id
    await db.commit()
    await db.refresh(task)
    return TaskResponseSchema.model_validate(task)


@router.delete(
    "/{task_id}/unassign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Unassign task from user"
)
async def unassign_task_from_user(
        task_id: int,
        user_id: int,
        db: AsyncSession = Depends(get_database_session)
) -> TaskResponseSchema:
    """
    Remove the task assignment from a specific user.
    """
    query = select(Task).where(Task.id.is_(task_id))
    result = await db.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    if task.assigned_user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task is not assigned to this user"
        )

    task.assigned_user_id = None
    await db.commit()
    await db.refresh(task)
    return TaskResponseSchema.model_validate(task)
