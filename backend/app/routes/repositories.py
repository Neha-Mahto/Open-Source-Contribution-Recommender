"""
Repository endpoints.

  POST /repositories/sync               Pull a repo + its issues from GitHub, compute health scores
  GET  /repositories                    List synced repos, ranked by health score
  GET  /repositories/meta/rate-limit    Check remaining GitHub API quota for the current user's token
  GET  /repositories/{id}               Single repo detail
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.repositories.repository_repository import RepositoryRepository
from app.schemas.repository import RepositoryOut, RepositorySyncOut
from app.services import github_client
from app.services.github_client import GitHubRateLimitError
from app.services.repository_sync import sync_repository

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.post("/sync", response_model=RepositorySyncOut)
async def sync_repo(
    full_name: str = Query(..., description="owner/repo, e.g. 'facebook/react'"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        result = await sync_repository(db, full_name, access_token=current_user.github_access_token)
    except GitHubRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"GitHub API rate limit exceeded. Try again after {exc.reset_at}.",
        )
    except Exception as exc:  # repo not found, network error, etc. -- surfaced as a clean 400
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sync failed: {exc}")

    return RepositorySyncOut(
        repository=result["repository"],
        issues_synced=result["issues_synced"],
        good_first_issues=result["good_first_issues"],
    )


@router.get("/meta/rate-limit")
async def rate_limit_status(current_user: User = Depends(get_current_user)):
    """Lets the frontend show 'X requests remaining' instead of users hitting a wall blind."""
    return await github_client.get_rate_limit_status(access_token=current_user.github_access_token)


@router.get("", response_model=list[RepositoryOut])
async def list_repositories(
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    return await RepositoryRepository(db).list_all(limit=limit, offset=offset)


@router.get("/{repo_id}", response_model=RepositoryOut)
async def get_repository(repo_id: int, db: AsyncSession = Depends(get_db)):
    repo = await RepositoryRepository(db).get_by_id(repo_id)
    if repo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repository not found")
    return repo
