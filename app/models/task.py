from datetime import datetime
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.group import Group
from .associations import task_group_association

if TYPE_CHECKING:
    from app.models.user import User


class Task(Base):
    """Task model representing a task in the system."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    assigned_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assigned_by_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    assigned_user = relationship(
        "User",
        back_populates="tasks",
        foreign_keys=[assigned_user_id],
    )
    assigned_by = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assigned_by_user_id],
    )
    assigned_groups: Mapped[List[Group]] = relationship(
        Group,
        secondary=task_group_association,
        back_populates="tasks",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - simple repr
        return f"Task(id={self.id}, title='{self.title}', completed={self.is_completed})"

