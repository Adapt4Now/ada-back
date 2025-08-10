from typing import List

from app.crud.family import FamilyRepository
from app.schemas.family import FamilyCreate, FamilyResponse
from app.core.exceptions import FamilyNotFoundError


class FamilyService:
    """Service layer for family-related operations."""

    def __init__(self, repo: FamilyRepository):
        self.repo = repo

    async def create_family(self, data: FamilyCreate) -> FamilyResponse:
        family = await self.repo.create(data)
        return FamilyResponse.model_validate(family)

    async def list_families(self) -> List[FamilyResponse]:
        families = await self.repo.get_all()
        return [FamilyResponse.model_validate(f) for f in families]

    async def get_family(self, family_id: int) -> FamilyResponse:
        family = await self.repo.get(family_id)
        if family is None:
            raise FamilyNotFoundError()
        return FamilyResponse.model_validate(family)
