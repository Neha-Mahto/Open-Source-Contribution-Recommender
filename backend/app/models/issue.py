from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import ARRAY, BigInteger, DateTime, Enum, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IssueDifficulty(str, PyEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)

    repository_id: Mapped[int] = mapped_column(ForeignKey("repositories.id", ondelete="CASCADE"), index=True)
    github_issue_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    number: Mapped[int] = mapped_column(Integer, nullable=False)  # issue number within the repo

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    body_excerpt: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)

    labels: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)

    difficulty: Mapped[IssueDifficulty] = mapped_column(
        Enum(IssueDifficulty, name="issue_difficulty"), default=IssueDifficulty.INTERMEDIATE
    )

    # Computed per-user at request time, but we cache the "global" base score
    # (independent of any specific user) here for fast initial sorting.
    base_score: Mapped[float] = mapped_column(Float, default=0.0)

    github_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_open: Mapped[bool] = mapped_column(default=True)

    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    repository: Mapped["Repository"] = relationship(back_populates="issues")
