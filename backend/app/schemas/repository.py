from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    description: str | None
    url: str
    primary_language: str | None
    topics: list[str] | None
    stars: int
    forks: int
    open_issues_count: int
    activity_score: float
    community_score: float
    friendliness_score: float
    overall_health_score: float
    last_synced_at: datetime | None


class RepositorySyncOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    repository: RepositoryOut
    issues_synced: int
    good_first_issues: int
