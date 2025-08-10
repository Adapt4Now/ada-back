from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class FamilyMembership(Base):
    __tablename__ = "family_memberships"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    family_id = Column(Integer, ForeignKey("families.id", ondelete="CASCADE"), primary_key=True)
    role = Column(String(50), nullable=False, server_default=text("'member'"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="family_memberships")
    family = relationship("Family", back_populates="premium_memberships")
