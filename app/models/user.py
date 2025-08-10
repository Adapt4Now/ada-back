
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    text,
)
from sqlalchemy import true
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from .associations import user_family_membership


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=true(), server_default=true())

    is_superuser = Column(Boolean, nullable=False, server_default=text('false'))
    is_premium = Column(Boolean, nullable=False, server_default=true())
    is_email_verified = Column(Boolean, nullable=False, server_default=text('false'))
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    first_name = Column(String(150), nullable=True)
    last_name = Column(String(150), nullable=True)
    avatar_url = Column(String, nullable=True)
    locale = Column(String(20), nullable=False, server_default=text("'en-US'"))
    timezone = Column(String(50), nullable=False, server_default=text("'UTC'"))
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    points = Column(Integer, nullable=False, server_default=text('0'))
    level = Column(SmallInteger, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    family_id = Column(Integer, ForeignKey("families.id", ondelete="SET NULL"), nullable=True)

    notifications = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
    settings = relationship(
        "Setting", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    # Tasks assigned to the user
    tasks = relationship(
        "Task",
        back_populates="assigned_user",
        cascade="all, delete-orphan",
    )
    # Tasks this user assigned to others
    assigned_tasks = relationship(
        "Task",
        back_populates="assigned_by",
        foreign_keys="Task.assigned_by_user_id",
        lazy="selectin",
    )

    family = relationship(
        "Family",
        back_populates="members",
        foreign_keys="User.family_id",
    )
    families = relationship(
        "Family",
        secondary=user_family_membership,
        back_populates="premium_members",
        lazy="selectin",
    )
    groups = relationship(
        "Group",
        secondary="user_group_membership",
        back_populates="users",
        lazy="selectin",
    )

    creator = relationship("User", remote_side=[id])
