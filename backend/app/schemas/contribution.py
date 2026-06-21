from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import ContributionStatus


class ContributionCreate(BaseModel):
    repository_full_name: str
    issue_or_pr_number: int
    title: str
    url: str
    status: ContributionStatus
    occurred_at: datetime | None = None  # defaults to "now" if omitted


class ContributionUpdate(BaseModel):
    status: ContributionStatus


class ContributionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    repository_full_name: str
    issue_or_pr_number: int
    title: str
    url: str
    status: ContributionStatus
    occurred_at: datetime
    created_at: datetime


class ContributionStats(BaseModel):
    issues_opened: int
    pr_submitted: int
    pr_merged: int
    pr_closed: int
    total: int
    roadmap_stage: int
    roadmap_label: str
