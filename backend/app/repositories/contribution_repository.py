"""Data-access layer for the Contribution model."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Contribution, ContributionStatus


class ContributionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, **kwargs) -> Contribution:
        contribution = Contribution(user_id=user_id, **kwargs)
        self.db.add(contribution)
        await self.db.commit()
        await self.db.refresh(contribution)
        return contribution

    async def get_by_id(self, contribution_id: int) -> Contribution | None:
        return await self.db.get(Contribution, contribution_id)

    async def list_by_user(self, user_id: int, status: ContributionStatus | None = None) -> list[Contribution]:
        query = select(Contribution).where(Contribution.user_id == user_id)
        if status:
            query = query.where(Contribution.status == status)
        query = query.order_by(Contribution.occurred_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_status(self, contribution: Contribution, status: ContributionStatus) -> Contribution:
        contribution.status = status
        await self.db.commit()
        await self.db.refresh(contribution)
        return contribution

    async def count_by_status(self, user_id: int) -> dict[str, int]:
        result = await self.db.execute(
            select(Contribution.status, func.count(Contribution.id))
            .where(Contribution.user_id == user_id)
            .group_by(Contribution.status)
        )
        counts = {status.value: 0 for status in ContributionStatus}
        for status, count in result.all():
            counts[status.value] = count
        return counts

    async def activity_timeline(self, user_id: int, days: int = 90) -> list[dict]:
        """Day-by-day contribution counts for the last N days, for a GitHub-style heatmap."""
        since = datetime.now(timezone.utc) - timedelta(days=days)
        result = await self.db.execute(
            select(Contribution.occurred_at).where(
                Contribution.user_id == user_id, Contribution.occurred_at >= since
            )
        )
        counts_by_day: dict[str, int] = defaultdict(int)
        for (occurred_at,) in result.all():
            counts_by_day[occurred_at.date().isoformat()] += 1

        return [{"date": day, "count": count} for day, count in sorted(counts_by_day.items())]
