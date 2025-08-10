from typing import List

from app.domain.families.repository import FamilyRepository
from app.domain.families.schemas import FamilyCreate, FamilyResponse
from app.core.exceptions import FamilyNotFoundError
from app.database import UnitOfWork


class FamilyService:
    """Service layer for family-related operations."""

    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_family(self, data: FamilyCreate) -> FamilyResponse:
        async with self.uow as uow:
            repo = FamilyRepository(uow.session)
            family = await repo.create(data)
            await uow.commit()
        return FamilyResponse.model_validate(family)

    async def list_families(self) -> List[FamilyResponse]:
        async with self.uow as uow:
            repo = FamilyRepository(uow.session)
            families = await repo.get_all()
        return [FamilyResponse.model_validate(f) for f in families]

    async def get_family(self, family_id: int) -> FamilyResponse:
        async with self.uow as uow:
            repo = FamilyRepository(uow.session)
            family = await repo.get(family_id)
        if family is None:
            raise FamilyNotFoundError()
        return FamilyResponse.model_validate(family)
