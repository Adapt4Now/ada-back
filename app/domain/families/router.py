from typing import List

from fastapi import APIRouter, Depends, status
from dependency_injector.wiring import inject, Provide

from app.domain.families.schemas import FamilyCreate, FamilyResponse
from app.domain.families.service import FamilyService
from app.dependencies import Container

router = APIRouter(prefix="/families", tags=["families"])


@router.post("/", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
@inject
async def create_family(
    family_data: FamilyCreate,
    service: FamilyService = Depends(Provide[Container.family_service]),
) -> FamilyResponse:
    return await service.create_family(family_data)


@router.get("/", response_model=List[FamilyResponse])
@inject
async def list_families(
    service: FamilyService = Depends(Provide[Container.family_service]),
) -> List[FamilyResponse]:
    return await service.list_families()


@router.get("/{family_id}", response_model=FamilyResponse)
@inject
async def get_family(
    family_id: int,
    service: FamilyService = Depends(Provide[Container.family_service]),
) -> FamilyResponse:
    return await service.get_family(family_id)
