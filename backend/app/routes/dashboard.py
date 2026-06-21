"""
Dashboard endpoint -- one call that aggregates everything the frontend
needs for the main personalized view: contribution stats + roadmap stage,
language breakdown, activity timeline, and bookmark collection summary.
"""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import User
from app.repositories.bookmark_repository import BookmarkRepository
from app.repositories.contribution_repository import ContributionRepository
from app.schemas.bookmark import CollectionSummary
from app.schemas.contribution import ContributionStats
from app.schemas.dashboard import ActivityDay, DashboardOut, LanguageBreakdownItem
from app.services.roadmap import determine_roadmap_stage

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    contribution_repo = ContributionRepository(db)
    bookmark_repo = BookmarkRepository(db)

    counts = await contribution_repo.count_by_status(current_user.id)
    stage, label = determine_roadmap_stage(counts)
    contribution_stats = ContributionStats(
        issues_opened=counts.get("issue_opened", 0),
        pr_submitted=counts.get("pr_submitted", 0),
        pr_merged=counts.get("pr_merged", 0),
        pr_closed=counts.get("pr_closed", 0),
        total=sum(counts.values()),
        roadmap_stage=stage,
        roadmap_label=label,
    )

    timeline_rows = await contribution_repo.activity_timeline(current_user.id, days=90)
    activity_timeline = [ActivityDay(date=row["date"], count=row["count"]) for row in timeline_rows]

    # Language breakdown is derived from the repos behind the user's bookmarked
    # issues -- a lightweight proxy for "what languages is this person engaging
    # with" until a dedicated sync of the user's own GitHub repos is added.
    bookmarks = await bookmark_repo.list_by_user(current_user.id)
    language_counter = Counter()
    for bookmark in bookmarks:
        if bookmark.issue and bookmark.issue.repository and bookmark.issue.repository.primary_language:
            language_counter[bookmark.issue.repository.primary_language] += 1
    language_breakdown = [
        LanguageBreakdownItem(language=lang, count=count) for lang, count in language_counter.most_common()
    ]

    collections_rows = await bookmark_repo.list_collections(current_user.id)
    bookmarked_collections = [
        CollectionSummary(collection_name=name, count=count) for name, count in collections_rows
    ]

    return DashboardOut(
        contribution_stats=contribution_stats,
        language_breakdown=language_breakdown,
        activity_timeline=activity_timeline,
        bookmarked_collections=bookmarked_collections,
        recent_bookmarks_count=len(bookmarks),
    )
