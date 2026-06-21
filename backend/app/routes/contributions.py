"""
Contribution tracker endpoints.

  POST  /contributions          Log a tracked event (issue opened, PR submitted/merged/closed)
  GET   /contributions          List the current user's tracked events
  GET   /contributions/stats    Aggregated counts + roadmap stage
  PATCH /contributions/{id}     Update status (e.g. pr_submitted -> pr_merged)
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import ContributionStatus, User
from app.repositories.contribution_repository import ContributionRepository
from app.schemas.contribution import ContributionCreate, ContributionOut, ContributionStats, ContributionUpdate
from app.services.roadmap import determine_roadmap_stage

router = APIRouter(prefix="/contributions", tags=["contributions"])


@router.post("", response_model=ContributionOut, status_code=status.HTTP_201_CREATED)
async def create_contribution(
    payload: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    occurred_at = payload.occurred_at or datetime.now(timezone.utc)
    return await ContributionRepository(db).create(
        user_id=current_user.id,
        repository_full_name=payload.repository_full_name,
        issue_or_pr_number=payload.issue_or_pr_number,
        title=payload.title,
        url=payload.url,
        status=payload.status,
        occurred_at=occurred_at,
    )


@router.get("", response_model=list[ContributionOut])
async def list_contributions(
    status_filter: ContributionStatus | None = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ContributionRepository(db).list_by_user(current_user.id, status=status_filter)


@router.get("/stats", response_model=ContributionStats)
async def get_contribution_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    counts = await ContributionRepository(db).count_by_status(current_user.id)
    stage, label = determine_roadmap_stage(counts)
    return ContributionStats(
        issues_opened=counts.get("issue_opened", 0),
        pr_submitted=counts.get("pr_submitted", 0),
        pr_merged=counts.get("pr_merged", 0),
        pr_closed=counts.get("pr_closed", 0),
        total=sum(counts.values()),
        roadmap_stage=stage,
        roadmap_label=label,
    )


@router.patch("/{contribution_id}", response_model=ContributionOut)
async def update_contribution(
    contribution_id: int,
    payload: ContributionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = ContributionRepository(db)
    contribution = await repo.get_by_id(contribution_id)
    if contribution is None or contribution.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contribution not found")
    return await repo.update_status(contribution, payload.status)
