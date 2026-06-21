from pydantic import BaseModel, ConfigDict

from app.models import IssueDifficulty


class IssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    url: str
    labels: list[str] | None
    difficulty: IssueDifficulty
    comments_count: int
    is_open: bool


class RecommendedIssueOut(BaseModel):
    id: int
    title: str
    url: str
    labels: list[str] | None
    difficulty: IssueDifficulty
    repository_full_name: str | None
    repository_health_score: float | None
    match_score: float
