from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base

if TYPE_CHECKING:
    from app.domain.users.models import User  # noqa: F401


class Setting(Base):
    """Model representing user settings."""

    __tablename__ = "settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    theme: Mapped[str] = mapped_column(String(50), default="light")
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notification_prefs: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
        default=dict,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="settings")
