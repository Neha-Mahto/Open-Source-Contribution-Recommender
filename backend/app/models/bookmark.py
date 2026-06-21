from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Bookmark(Base):
    """
    A user saving an issue, optionally grouped into a named collection
    (e.g. "Hacktoberfest Targets", "Backend Projects").
    """

    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "issue_id", name="uq_user_issue_bookmark"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id", ondelete="CASCADE"), index=True)

    collection_name: Mapped[str] = mapped_column(String(255), default="Default")
    note: Mapped[str | None] = mapped_column(String(512), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="bookmarks")
    issue: Mapped["Issue"] = relationship()
