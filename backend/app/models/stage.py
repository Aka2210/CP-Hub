from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.db import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    requires: Mapped[list] = mapped_column(JSON, default=list)
    problems: Mapped[list] = mapped_column(JSON, default=list)
    rewards_exp: Mapped[int] = mapped_column(default=0)
    rewards_coins: Mapped[int] = mapped_column(default=0)
