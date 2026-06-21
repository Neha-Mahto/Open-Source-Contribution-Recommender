from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Repository(Base):
    """
    Cached snapshot of a GitHub repository.

    We don't hit the GitHub API live on every request -- a background sync
    job refreshes rows here periodically, and everything else reads from
    this table (with Redis as a faster cache in front of it).
    """

    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(primary_key=True)

    github_repo_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)  # "owner/repo"
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    url: Mapped[str] = mapped_column(String(512), nullable=False)

    primary_language: Mapped[str | None] = mapped_column(String(100), nullable=True)
    topics: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    stars: Mapped[int] = mapped_column(Integer, default=0)
    forks: Mapped[int] = mapped_column(Integer, default=0)
    open_issues_count: Mapped[int] = mapped_column(Integer, default=0)

    last_commit_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_release_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # --- Computed health score components (0-100 each), recalculated on sync ---
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    community_score: Mapped[float] = mapped_column(Float, default=0.0)
    friendliness_score: Mapped[float] = mapped_column(Float, default=0.0)
    overall_health_score: Mapped[float] = mapped_column(Float, default=0.0)

    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    issues: Mapped[list["Issue"]] = relationship(back_populates="repository", cascade="all, delete-orphan")
