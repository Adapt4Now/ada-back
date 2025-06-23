from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.family import Family
from app.models.group import Group
from app.models.associations import user_group_membership, user_family_membership
from app.schemas.family import FamilyCreate


async def create_family(db: AsyncSession, family: FamilyCreate) -> Family:
    db_family = Family(name=family.name, created_by=family.created_by)
    db.add(db_family)
    await db.commit()
    await db.refresh(db_family)

    # create default group
    default_group = Group(
        name="general",
        description="Default group",
        created_by="system",
        family_id=db_family.id,
    )
    db.add(default_group)
    await db.commit()
    await db.refresh(default_group)

    # add creator to default group
    await db.execute(
        user_group_membership.insert().values(
            user_id=family.created_by, group_id=default_group.id
        )
    )
    # add creator to family membership
    await db.execute(
        user_family_membership.insert().values(
            user_id=family.created_by, family_id=db_family.id
        )
    )
    await db.commit()

    return db_family


async def get_family(db: AsyncSession, family_id: int) -> Family | None:
    result = await db.execute(select(Family).where(Family.id == family_id))
    return result.scalar_one_or_none()


async def get_families(db: AsyncSession) -> list[Family]:
    result = await db.execute(select(Family))
    return list(result.scalars().all())
