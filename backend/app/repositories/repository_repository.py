"""Data-access layer for the Repository model (the cached GitHub repo table)."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Repository
from app.utils.github_helpers import parse_github_datetime


class RepositoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, repo_id: int) -> Repository | None:
        return await self.db.get(Repository, repo_id)

    async def get_by_full_name(self, full_name: str) -> Repository | None:
        result = await self.db.execute(select(Repository).where(Repository.full_name == full_name))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> list[Repository]:
        result = await self.db.execute(
            select(Repository).order_by(Repository.overall_health_score.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def upsert_from_github(self, github_data: dict) -> Repository:
        """
        Create or refresh a repo row from a raw GitHub API repo payload.
        Note: GitHub's `pushed_at` is the best available proxy for "last commit"
        without an extra API call to the commits endpoint.
        """
        existing = await self.get_by_full_name(github_data["full_name"])

        fields = dict(
            github_repo_id=github_data["id"],
            full_name=github_data["full_name"],
            description=github_data.get("description"),
            url=github_data["html_url"],
            primary_language=github_data.get("language"),
            topics=github_data.get("topics") or [],
            stars=github_data.get("stargazers_count", 0),
            forks=github_data.get("forks_count", 0),
            open_issues_count=github_data.get("open_issues_count", 0),
            last_commit_at=parse_github_datetime(github_data.get("pushed_at")),
            last_synced_at=datetime.now(timezone.utc),
        )

        if existing:
            for key, value in fields.items():
                setattr(existing, key, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        repo = Repository(**fields)
        self.db.add(repo)
        await self.db.commit()
        await self.db.refresh(repo)
        return repo

    async def update_health_scores(
        self, repo: Repository, activity: float, community: float, friendliness: float, overall: float
    ) -> Repository:
        repo.activity_score = activity
        repo.community_score = community
        repo.friendliness_score = friendliness
        repo.overall_health_score = overall
        await self.db.commit()
        await self.db.refresh(repo)
        return repo
