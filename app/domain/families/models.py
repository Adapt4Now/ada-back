from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.domain.users.models import User
    from app.domain.groups.models import Group
    from .membership import FamilyMembership as FamilyMembershipType


class Family(Base):
    __tablename__ = "families"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    created_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    members: Mapped[List["User"]] = relationship(
        "User",
        back_populates="family",
        foreign_keys="User.family_id",
    )
    premium_memberships: Mapped[List["FamilyMembershipType"]] = relationship(
        "FamilyMembership",
        back_populates="family",
        cascade="all, delete-orphan",
    )
    premium_members: Mapped[List["User"]] = relationship(
        "User",
        secondary="family_memberships",
        back_populates="families",
        lazy="selectin",
        viewonly=True,
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="family", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Family(id={self.id}, name='{self.name}')"
