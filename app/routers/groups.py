from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse
from app.crud.group import (
    create_group as crud_create_group,
    get_group as crud_get_group,
    get_groups as crud_get_groups,
    update_group as crud_update_group,
    delete_group as crud_delete_group,
    add_users_to_group as crud_add_users_to_group,
    remove_users_from_group as crud_remove_users_from_group,
)

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

async def get_group_or_404(
    group_id: int,
    db: AsyncSession
) -> Group:
    """Get a group by id or raise 404 exception."""
    group = await crud_get_group(db, group_id, active_only=False)

    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found"
        )
    return group


@router.get(
    "/",
    response_model=List[GroupResponse],
    summary="Get all groups",
    description="Retrieve all groups from the system."
)
async def get_groups(
    db: AsyncSession = Depends(get_database_session)
) -> List[GroupResponse]:
    groups = await crud_get_groups(db)
    return [GroupResponse.model_validate(group) for group in groups]


@router.post(
    "/",
    response_model=GroupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new group",
    description="Create a new group with the provided data."
)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_database_session)
) -> GroupResponse:
    new_group = await crud_create_group(db, group_data)
    return GroupResponse.model_validate(new_group)


@router.delete(
    "/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete group",
    description="Delete a group from the system."
)
async def delete_group(
    group_id: Annotated[int, Path(gt=0)],
    db: AsyncSession = Depends(get_database_session)
) -> None:
    group = await crud_delete_group(db, group_id)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )


@router.put(
    "/{group_id}",
    response_model=GroupResponse,
    summary="Update group",
    description="Update group information."
)
async def update_group(
    group_id: Annotated[int, Path(gt=0)],
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_database_session)
) -> GroupResponse:
    group = await crud_update_group(db, group_id, group_data)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )
    return GroupResponse.model_validate(group)


@router.post(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Add user to group",
    description="Add a user to a specific group."
)
async def add_user_to_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    db: AsyncSession = Depends(get_database_session)
) -> GroupResponse:
    group = await crud_get_group(db, group_id, active_only=False)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )

    if user_id in group.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already in group {group_id}",
        )

    updated_group = await crud_add_users_to_group(db, group_id, [user_id])
    assert updated_group is not None  # for type checkers
    return GroupResponse.model_validate(updated_group)


@router.delete(
    "/{group_id}/users/{user_id}",
    response_model=GroupResponse,
    summary="Remove user from group",
    description="Remove a user from a specific group."
)
async def remove_user_from_group(
    group_id: Annotated[int, Path(gt=0)],
    user_id: Annotated[int, Path(gt=0)],
    db: AsyncSession = Depends(get_database_session)
) -> GroupResponse:
    group = await crud_get_group(db, group_id, active_only=False)
    if group is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {group_id} not found",
        )

    if user_id not in group.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is not in group {group_id}",
        )

    updated_group = await crud_remove_users_from_group(db, group_id, [user_id])
    assert updated_group is not None
    return GroupResponse.model_validate(updated_group)
