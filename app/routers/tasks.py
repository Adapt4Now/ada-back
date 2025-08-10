from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.task import TaskRepository
from app.database import get_database_session
from app.schemas.task import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    TaskAssignGroupsSchema,
    TaskAssignUserSchema,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_repository(
    db: AsyncSession = Depends(get_database_session),
) -> TaskRepository:
    return TaskRepository(db)


@router.get(
    "/",
    response_model=List[TaskResponseSchema],
    summary="Get all tasks",
)
async def get_tasks(
    include_archived: bool = False,
    repo: TaskRepository = Depends(get_task_repository),
) -> List[TaskResponseSchema]:
    """Retrieve all tasks from the system."""
    return await repo.get_all(include_archived)


@router.post(
    "/",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
)
async def create_task(
    task_data: TaskCreateSchema,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Create a new task with the provided data."""
    return await repo.create(task_data)


@router.get(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Get task by ID",
)
async def get_task_by_id(
    task_id: int,
    include_archived: bool = False,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Get detailed information about a specific task."""
    return await repo.get_by_id(task_id, include_archived)


@router.put(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Update task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Update task information."""
    return await repo.update(task_id, task_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
async def delete_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
) -> None:
    """Delete a task from the system."""
    await repo.delete(task_id)


@router.post(
    "/{task_id}/assign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Assign task to user",
)
async def assign_task_to_user(
    task_id: int,
    user_id: int,
    assignment: TaskAssignUserSchema,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Assign a task to a specific user."""
    return await repo.assign_to_user(task_id, user_id, assignment.assigned_by_user_id)


@router.delete(
    "/{task_id}/unassign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Unassign task from user",
)
async def unassign_task_from_user(
    task_id: int,
    user_id: int,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Remove the task assignment from a specific user."""
    return await repo.unassign_from_user(task_id, user_id)


@router.post(
    "/{task_id}/assign/groups",
    response_model=TaskResponseSchema,
    summary="Assign task to groups",
)
async def assign_task_to_groups(
    task_id: int,
    assignment: TaskAssignGroupsSchema,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Assign a task to multiple groups."""
    return await repo.assign_to_groups(task_id, list(assignment.group_ids))


@router.delete(
    "/{task_id}/unassign/group/{group_id}",
    response_model=TaskResponseSchema,
    summary="Unassign task from group",
)
async def unassign_task_from_group(
    task_id: int,
    group_id: int,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Remove the task assignment from a specific group."""
    return await repo.unassign_from_group(task_id, group_id)


@router.post(
    "/{task_id}/restore",
    response_model=TaskResponseSchema,
    summary="Restore archived task",
)
async def restore_task(
    task_id: int,
    repo: TaskRepository = Depends(get_task_repository),
) -> TaskResponseSchema:
    """Restore a previously archived task."""
    return await repo.restore(task_id)
