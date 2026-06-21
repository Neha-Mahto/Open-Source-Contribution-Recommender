"""
Issue endpoints.

  GET /issues               List synced issues
  GET /issues/recommended   Personalized recommendations for the logged-in user
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.repositories.issue_repository import IssueRepository
from app.schemas.issue import IssueOut, RecommendedIssueOut
from app.services.recommendation import rank_issues_for_user

router = APIRouter(prefix="/issues", tags=["issues"])


@router.get("", response_model=list[IssueOut])
async def list_issues(
    limit: int = Query(50, le=200),
    repository_id: int | None = Query(None, description="Filter to issues belonging to one synced repo"),
    db: AsyncSession = Depends(get_db),
):
    if repository_id is not None:
        issues = await IssueRepository(db).list_by_repository(repository_id)
        return issues[:limit]
    return await IssueRepository(db).list_open_with_repository(limit=limit)


@router.get("/recommended", response_model=list[RecommendedIssueOut])
async def get_recommended_issues(
    limit: int = Query(20, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ranks every synced open issue against the current user's known
    languages, label friendliness, repo health, and freshness.
    See app/services/recommendation.py for the scoring breakdown.
    """
    candidate_pool = await IssueRepository(db).list_open_with_repository(limit=500)
    ranked = rank_issues_for_user(candidate_pool, current_user)

    return [
        RecommendedIssueOut(
            id=issue.id,
            title=issue.title,
            url=issue.url,
            labels=issue.labels,
            difficulty=issue.difficulty,
            repository_full_name=issue.repository.full_name if issue.repository else None,
            repository_health_score=issue.repository.overall_health_score if issue.repository else None,
            match_score=score,
        )
        for issue, score in ranked[:limit]
    ]
