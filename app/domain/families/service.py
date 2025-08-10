from typing import List
import logging

from app.domain.families.schemas import FamilyCreate, FamilyResponse
from app.core.exceptions import FamilyNotFoundError
from app.database import UnitOfWork

logger = logging.getLogger(__name__)


class FamilyService:
    """Service layer for family-related operations."""

    def __init__(self, repository_factory, unit_of_work: UnitOfWork):
        self.repository_factory = repository_factory
        self.unit_of_work = unit_of_work

    async def create_family(self, data: FamilyCreate) -> FamilyResponse:
        """Create a new family."""
        logger.info("Creating family")
        async with self.unit_of_work as unit_of_work:
            family_repository = self.repository_factory(unit_of_work.session)
            family = await family_repository.create(data)
        logger.info("Created family %s", family.id)
        return FamilyResponse.model_validate(family)

    async def list_families(self) -> List[FamilyResponse]:
        """List all families."""
        async with self.unit_of_work as unit_of_work:
            family_repository = self.repository_factory(unit_of_work.session)
            families = await family_repository.get_all()
        return [FamilyResponse.model_validate(f) for f in families]

    async def get_family(self, family_id: int) -> FamilyResponse:
        """Retrieve a family by id."""
        async with self.unit_of_work as unit_of_work:
            family_repository = self.repository_factory(unit_of_work.session)
            family = await family_repository.get(family_id)
        if family is None:
            raise FamilyNotFoundError()
        return FamilyResponse.model_validate(family)
