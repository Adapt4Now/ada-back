from typing import List
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.family import FamilyCreate, FamilyResponse
from app.crud.family import FamilyRepository

router = APIRouter(prefix="/families", tags=["families"])


def get_family_repository(
    db: AsyncSession = Depends(get_database_session),
) -> FamilyRepository:
    return FamilyRepository(db)


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    repo: FamilyRepository = Depends(get_family_repository),
) -> FamilyResponse:
    new_family = await repo.create(family_data)
    return FamilyResponse.model_validate(new_family)


@router.get("/", response_model=List[FamilyResponse])
async def list_families(
    repo: FamilyRepository = Depends(get_family_repository),
) -> List[FamilyResponse]:
    families = await repo.get_all()
    return [FamilyResponse.model_validate(f) for f in families]


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int,
    repo: FamilyRepository = Depends(get_family_repository),
) -> FamilyResponse:
    family = await repo.get(family_id)
    if family is None:
        raise HTTPException(status_code=404, detail="Family not found")
    return FamilyResponse.model_validate(family)
