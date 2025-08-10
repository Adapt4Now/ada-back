from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.domain.users.models import User


user_achievements = Table(
    "user_achievements",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "achievement_id",
        Integer,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "awarded_at",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    ),
)


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_achievements,
        back_populates="achievements",
        lazy="selectin",
    )
