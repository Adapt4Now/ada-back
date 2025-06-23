from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.family import FamilyCreate, FamilyResponse
from app.crud.family import (
    create_family as crud_create_family,
    get_family as crud_get_family,
    get_families as crud_get_families,
)

router = APIRouter(prefix="/families", tags=["families"])


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    db: AsyncSession = Depends(get_database_session),
) -> FamilyResponse:
    new_family = await crud_create_family(db, family_data)
    return FamilyResponse.model_validate(new_family)


@router.get("/", response_model=List[FamilyResponse])
async def list_families(db: AsyncSession = Depends(get_database_session)) -> List[FamilyResponse]:
    families = await crud_get_families(db)
    return [FamilyResponse.model_validate(f) for f in families]


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int,
    db: AsyncSession = Depends(get_database_session),
) -> FamilyResponse:
    family = await crud_get_family(db, family_id)
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return FamilyResponse.model_validate(family)
