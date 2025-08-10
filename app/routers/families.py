from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_database_session
from app.schemas.family import FamilyCreate, FamilyResponse
from app.services import FamilyService
from app.crud.family import FamilyRepository

router = APIRouter(prefix="/families", tags=["families"])


def get_family_service(
    db: AsyncSession = Depends(get_database_session),
) -> FamilyService:
    repo = FamilyRepository(db)
    return FamilyService(repo)


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    service: FamilyService = Depends(get_family_service),
) -> FamilyResponse:
    return await service.create_family(family_data)


@router.get("/", response_model=List[FamilyResponse])
async def list_families(
    service: FamilyService = Depends(get_family_service),
) -> List[FamilyResponse]:
    return await service.list_families()


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: int,
    service: FamilyService = Depends(get_family_service),
) -> FamilyResponse:
    return await service.get_family(family_id)
