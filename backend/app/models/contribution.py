from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContributionStatus(str, PyEnum):
    ISSUE_OPENED = "issue_opened"
    PR_SUBMITTED = "pr_submitted"
    PR_MERGED = "pr_merged"
    PR_CLOSED = "pr_closed"


class Contribution(Base):
    """
    A single tracked contribution event, used to build the user's
    progress dashboard and contribution roadmap stage.
    """

    __tablename__ = "contributions"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    repository_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    issue_or_pr_number: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)

    status: Mapped[ContributionStatus] = mapped_column(Enum(ContributionStatus, name="contribution_status"))

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="contributions")
