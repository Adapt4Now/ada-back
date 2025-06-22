from datetime import datetime
from typing import Optional, List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.group import Group

task_group_association = Table(
    'task_groups',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True),
    Column('group_id', Integer, ForeignKey('groups.id', ondelete="CASCADE"), primary_key=True)
)


class Task(Base):
    """
    Task model representing a task in the system.
    
    Attributes:
        id: Unique task identifier
        title: Task title
        description: Detailed task description
        is_completed: Task completion status
        priority: Task priority (1-5)
        created_at: Creation timestamp
        updated_at: Last update timestamp
        completed_at: Completion timestamp
        assigned_user_id: ID of the assigned user
        assigned_user: Related user object
        assigned_groups: List of groups the task is assigned to
    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[int] = mapped_column(Integer, default=1)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    assigned_user_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    assigned_user = relationship("User", back_populates="tasks")
    assigned_groups: Mapped[List[Group]] = relationship(
        Group,
        secondary=task_group_association,
        back_populates="tasks",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', completed={self.is_completed})"
