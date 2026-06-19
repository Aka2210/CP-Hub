import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.db import Base

if TYPE_CHECKING:
    from backend.app.models.user import User


class PlatformStatsCache(Base):
    __tablename__ = "platform_stats_cache"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    leetcode_easy: Mapped[int | None] = mapped_column(default=None)
    leetcode_medium: Mapped[int | None] = mapped_column(default=None)
    leetcode_hard: Mapped[int | None] = mapped_column(default=None)
    leetcode_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    codeforces_solved: Mapped[int | None] = mapped_column(default=None)
    codeforces_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)

    user: Mapped["User"] = relationship(back_populates="platform_stats")
