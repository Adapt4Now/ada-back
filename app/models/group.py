from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .associations import task_group_association, user_group_membership
from sqlalchemy.sql import func

from app.database import Base

# Use TYPE_CHECKING for type imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.task import Task
    from app.models.user import User


class Group(Base):
    """
    Group model representing a team or department in the system.
    
    Attributes:
        id: Unique group identifier
        name: Group name (1-100 chars)
        description: Optional group description
        created_by: Username of group creator
        created_at: Timestamp of group creation
        updated_at: Optional timestamp of last update
        is_active: Flag indicating if a group is active
        tasks: List of tasks assigned to the group
    """

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(
        Integer, 
        primary_key=True, 
        index=True,
        autoincrement=True
    )
    name: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        unique=True,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, 
        nullable=True
    )
    created_by: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )
    family_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    family = relationship("Family", back_populates="groups")
    users: Mapped[List["User"]] = relationship(
        "User",
        secondary=user_group_membership,
        back_populates="groups",
        lazy="selectin",
    )

    # Relationship with Task via association table
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        secondary=task_group_association,
        back_populates="assigned_groups",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return (
            f"Group(id={self.id}, "
            f"name='{self.name}', "
            f"created_by='{self.created_by}', "
            f"is_active={self.is_active})"
        )

