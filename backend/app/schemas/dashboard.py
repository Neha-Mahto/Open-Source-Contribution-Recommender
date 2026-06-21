from pydantic import BaseModel

from app.schemas.bookmark import CollectionSummary
from app.schemas.contribution import ContributionStats


class LanguageBreakdownItem(BaseModel):
    language: str
    count: int


class ActivityDay(BaseModel):
    date: str  # ISO date, e.g. "2026-06-15"
    count: int


class DashboardOut(BaseModel):
    contribution_stats: ContributionStats
    language_breakdown: list[LanguageBreakdownItem]
    activity_timeline: list[ActivityDay]
    bookmarked_collections: list[CollectionSummary]
    recent_bookmarks_count: int
