from typing import List
from fastapi import APIRouter, Depends, status

from app.dependencies import container
from .schemas import (
    TaskCreateSchema,
    TaskResponseSchema,
    TaskUpdateSchema,
    TaskAssignGroupsSchema,
    TaskAssignUserSchema,
)
from .service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "/",
    response_model=List[TaskResponseSchema],
    summary="Get all tasks",
)
async def get_tasks(
    include_archived: bool = False,
    service: TaskService = Depends(container.task_service),
) -> List[TaskResponseSchema]:
    """Retrieve all tasks from the system."""
    return await service.get_tasks(include_archived)


@router.post(
    "/",
    response_model=TaskResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create new task",
)
async def create_task(
    task_data: TaskCreateSchema,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Create a new task with the provided data."""
    return await service.create_task(task_data)


@router.get(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Get task by ID",
)
async def get_task_by_id(
    task_id: int,
    include_archived: bool = False,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Get detailed information about a specific task."""
    return await service.get_task_by_id(task_id, include_archived)


@router.put(
    "/{task_id}",
    response_model=TaskResponseSchema,
    summary="Update task",
)
async def update_task(
    task_id: int,
    task_data: TaskUpdateSchema,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Update task information."""
    return await service.update_task(task_id, task_data)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete task",
)
async def delete_task(
    task_id: int,
    service: TaskService = Depends(container.task_service),
) -> None:
    """Delete a task from the system."""
    await service.delete_task(task_id)


@router.post(
    "/{task_id}/assign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Assign task to user",
)
async def assign_task_to_user(
    task_id: int,
    user_id: int,
    assignment: TaskAssignUserSchema,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Assign a task to a specific user."""
    return await service.assign_task_to_user(task_id, user_id, assignment)


@router.delete(
    "/{task_id}/unassign/user/{user_id}",
    response_model=TaskResponseSchema,
    summary="Unassign task from user",
)
async def unassign_task_from_user(
    task_id: int,
    user_id: int,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Remove the task assignment from a specific user."""
    return await service.unassign_task_from_user(task_id, user_id)


@router.post(
    "/{task_id}/assign/groups",
    response_model=TaskResponseSchema,
    summary="Assign task to groups",
)
async def assign_task_to_groups(
    task_id: int,
    assignment: TaskAssignGroupsSchema,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Assign a task to multiple groups."""
    return await service.assign_task_to_groups(task_id, assignment)


@router.delete(
    "/{task_id}/unassign/group/{group_id}",
    response_model=TaskResponseSchema,
    summary="Unassign task from group",
)
async def unassign_task_from_group(
    task_id: int,
    group_id: int,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Remove the task assignment from a specific group."""
    return await service.unassign_task_from_group(task_id, group_id)


@router.post(
    "/{task_id}/restore",
    response_model=TaskResponseSchema,
    summary="Restore archived task",
)
async def restore_task(
    task_id: int,
    service: TaskService = Depends(container.task_service),
) -> TaskResponseSchema:
    """Restore a previously archived task."""
    return await service.restore_task(task_id)
