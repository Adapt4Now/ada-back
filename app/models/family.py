from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base
from .associations import user_family_membership

if TYPE_CHECKING:
    from .user import User
    from .group import Group


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
    premium_members: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_family_membership,
        back_populates="families",
        lazy="selectin",
    )
    groups: Mapped[List["Group"]] = relationship(
        "Group", back_populates="family", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Family(id={self.id}, name='{self.name}')"
