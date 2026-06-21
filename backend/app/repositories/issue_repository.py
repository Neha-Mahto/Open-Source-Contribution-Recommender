"""Data-access layer for the Issue model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Issue, IssueDifficulty
from app.utils.github_helpers import parse_github_datetime


class IssueRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, issue_id: int) -> Issue | None:
        result = await self.db.execute(
            select(Issue).where(Issue.id == issue_id).options(selectinload(Issue.repository))
        )
        return result.scalar_one_or_none()

    async def list_by_repository(self, repository_id: int, is_open: bool = True) -> list[Issue]:
        result = await self.db.execute(
            select(Issue).where(Issue.repository_id == repository_id, Issue.is_open.is_(is_open))
        )
        return list(result.scalars().all())

    async def list_open_with_repository(self, limit: int = 100) -> list[Issue]:
        """
        Used by both the issue listing endpoint and the recommendation
        engine -- pulls open issues plus their parent repo in one query
        (selectinload avoids an N+1 when we read issue.repository.* later).
        """
        result = await self.db.execute(
            select(Issue)
            .where(Issue.is_open.is_(True))
            .options(selectinload(Issue.repository))
            .order_by(Issue.base_score.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def upsert_from_github(
        self,
        repository_id: int,
        github_data: dict,
        difficulty: IssueDifficulty,
        base_score: float,
    ) -> Issue:
        result = await self.db.execute(select(Issue).where(Issue.github_issue_id == github_data["id"]))
        existing = result.scalar_one_or_none()

        fields = dict(
            repository_id=repository_id,
            github_issue_id=github_data["id"],
            number=github_data["number"],
            title=github_data["title"],
            body_excerpt=(github_data.get("body") or "")[:1000] or None,
            url=github_data["html_url"],
            labels=[label["name"] for label in github_data.get("labels", [])],
            comments_count=github_data.get("comments", 0),
            difficulty=difficulty,
            base_score=base_score,
            is_open=github_data.get("state") == "open",
            last_synced_at=parse_github_datetime(github_data.get("updated_at")),
        )

        if existing:
            for key, value in fields.items():
                setattr(existing, key, value)
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        issue = Issue(
            github_created_at=parse_github_datetime(github_data.get("created_at")),
            **fields,
        )
        self.db.add(issue)
        await self.db.commit()
        await self.db.refresh(issue)
        return issue
