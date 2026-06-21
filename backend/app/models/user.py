from datetime import datetime

from sqlalchemy import ARRAY, BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    # GitHub identity
    github_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    github_username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Used by the recommendation engine to match issues to the user.
    # e.g. ["python", "javascript", "go"] -- derived from their repos on sync.
    known_languages: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Raw GitHub OAuth access token (encrypt at rest in production -- see README)
    github_access_token: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    bookmarks: Mapped[list["Bookmark"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    contributions: Mapped[list["Contribution"]] = relationship(back_populates="user", cascade="all, delete-orphan")
