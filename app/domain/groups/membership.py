from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class GroupMembership(Base):
    __tablename__ = "group_memberships"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(50), nullable=False, server_default=text("'member'"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="group_memberships")
    group = relationship("Group", back_populates="memberships")
