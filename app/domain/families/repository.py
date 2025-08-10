from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.families.models import Family
from app.domain.groups.membership import GroupMembership
from app.domain.families.membership import FamilyMembership
from app.domain.families.schemas import FamilyCreate
from app.domain.groups.models import Group


class FamilyRepository:
    """Repository for managing families."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, family: FamilyCreate) -> Family:
        db_family = Family(name=family.name, created_by=family.created_by)
        self.db.add(db_family)

        default_group = Group(
            name="general",
            description="Default group",
            created_by="system",
            family_id=db_family.id,
        )
        self.db.add(default_group)

        self.db.add(
            GroupMembership(user_id=family.created_by, group_id=default_group.id, role="owner")
        )
        self.db.add(
            FamilyMembership(user_id=family.created_by, family_id=db_family.id, role="owner")
        )

        return db_family

    async def get(self, family_id: int) -> Family | None:
        result = await self.db.execute(select(Family).where(Family.id == family_id))
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Family]:
        result = await self.db.execute(select(Family))
        return list(result.scalars().all())
