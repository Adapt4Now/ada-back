from typing import Annotated, List

from fastapi import APIRouter, Depends, Path, status

from app.dependencies import get_group_service

from .schemas import GroupCreate, GroupUpdate, GroupResponse
from .service import GroupService

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get(
    "/",
    response_model=List[GroupResponse],
    summary="Get all groups",
    description="Retrieve all groups from the system.",
)
async def get_groups(
    service: GroupService = Depends(get_group_service),
) -> List[GroupResponse]:
    return await service.get_groups()


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new group",
    description="Create a new group with the provided data.",
)
async def create_group(
    group_data: GroupCreate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    return await service.create_group(group_data)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group",
    description="Delete a group from the system.",
)
async def delete_group(
    group_id: Annotated[int, Path(gt=0)],
    service: GroupService = Depends(get_group_service),
) -> None:
    await service.delete_group(group_id)


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group",
    description="Update group information.",
)
async def update_group(
    group_id: Annotated[int, Path(gt=0)],
    group_data: GroupUpdate,
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    return await service.update_group(group_id, group_data)


@router.post(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Add user to group",
    description="Add a user to a specific group.",
)
async def add_user_to_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    return await service.add_user_to_group(group_id, user_id)


@router.delete(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Remove user from group",
    description="Remove a user from a specific group.",
)
async def remove_user_from_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    service: GroupService = Depends(get_group_service),
) -> GroupResponse:
    return await service.remove_user_from_group(group_id, user_id)
