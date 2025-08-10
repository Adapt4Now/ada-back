from typing import List, Annotated

from fastapi import APIRouter, Depends, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.crud.group import GroupRepository
from app.core.exceptions import GroupNotFoundError

router = APIRouter(prefix="/groups", tags=["groups"])


def get_group_repository(
    db: AsyncSession = Depends(get_database_session),
) -> GroupRepository:
    return GroupRepository(db)


async def get_group_or_404(
    group_id: int,
    repo: GroupRepository = Depends(get_group_repository),
) -> Group:
    group = await repo.get(group_id, active_only=False)
    if group is None:
        raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
    return group


@router.get(
    "/",
    response_model=List[GroupResponse],
    summary="Get all groups",
    description="Retrieve all groups from the system.",
)
async def get_groups(
    repo: GroupRepository = Depends(get_group_repository),
) -> List[GroupResponse]:
    groups = await repo.get_list()
    return [GroupResponse.model_validate(group) for group in groups]


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new group",
    description="Create a new group with the provided data.",
)
async def create_group(
    group_data: GroupCreate,
    repo: GroupRepository = Depends(get_group_repository),
) -> GroupResponse:
    new_group = await repo.create(group_data)
    return GroupResponse.model_validate(new_group)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group",
    description="Delete a group from the system.",
)
async def delete_group(
    group_id: Annotated[int, Path(gt=0)],
    repo: GroupRepository = Depends(get_group_repository),
) -> None:
    group = await repo.delete(group_id)
    if group is None:
        raise GroupNotFoundError(detail=f"Group with id {group_id} not found")


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group",
    description="Update group information.",
)
async def update_group(
    group_id: Annotated[int, Path(gt=0)],
    group_data: GroupUpdate,
    repo: GroupRepository = Depends(get_group_repository),
) -> GroupResponse:
    group = await repo.update(group_id, group_data)
    if group is None:
        raise GroupNotFoundError(detail=f"Group with id {group_id} not found")
    return GroupResponse.model_validate(group)


@router.post(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Add user to group",
    description="Add a user to a specific group.",
)
async def add_user_to_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    repo: GroupRepository = Depends(get_group_repository),
) -> GroupResponse:
    group = await get_group_or_404(group_id, repo)
    updated_group = await repo.add_users(group_id, {user_id: "member"})
    assert updated_group is not None
    return GroupResponse.model_validate(updated_group)


@router.delete(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Remove user from group",
    description="Remove a user from a specific group.",
)
async def remove_user_from_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    repo: GroupRepository = Depends(get_group_repository),
) -> GroupResponse:
    group = await get_group_or_404(group_id, repo)
    updated_group = await repo.remove_users(group_id, [user_id])
    assert updated_group is not None
    return GroupResponse.model_validate(updated_group)
