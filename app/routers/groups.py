from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.models.group import Group
from app.schemas.group import GroupCreate, GroupUpdate, GroupResponse

router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

async def get_group_or_404(
    group_id: int,
    db: AsyncSession
) -> Group:
    """Get a group by id or raise 404 exception."""
    query = select(Group).where(Group.id == group_id)
    result = await db.execute(query)
    group = result.scalar_one_or_none()

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
    query = select(Group)
    result = await db.execute(query)
    groups = result.scalars().all()
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
    new_group = Group(**group_data.model_dump())
    db.add(new_group)
    await db.commit()
    await db.refresh(new_group)
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
    group = await get_group_or_404(group_id, db)
    await db.delete(group)
    await db.commit()


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
    group = await get_group_or_404(group_id, db)
    
    update_data = group_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(group, field, value)

    await db.commit()
    await db.refresh(group)
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
    group = await get_group_or_404(group_id, db)
    
    if user_id in group.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is already in group {group_id}"
        )

    group.user_ids.append(user_id)
    await db.commit()
    await db.refresh(group)
    return GroupResponse.model_validate(group)


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
    group = await get_group_or_404(group_id, db)

    if user_id not in group.user_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_id} is not in group {group_id}"
        )

    group.user_ids.remove(user_id)
    await db.commit()
    await db.refresh(group)
    return GroupResponse.model_validate(group)