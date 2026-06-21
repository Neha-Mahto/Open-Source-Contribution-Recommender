"""Data-access layer for the Bookmark model."""

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Bookmark, Issue


class BookmarkRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, bookmark_id: int) -> Bookmark | None:
        result = await self.db.execute(
            select(Bookmark)
            .where(Bookmark.id == bookmark_id)
            .options(selectinload(Bookmark.issue).selectinload(Issue.repository))
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: int, collection_name: str | None = None) -> list[Bookmark]:
        query = (
            select(Bookmark)
            .where(Bookmark.user_id == user_id)
            .options(selectinload(Bookmark.issue).selectinload(Issue.repository))
            .order_by(Bookmark.created_at.desc())
        )
        if collection_name:
            query = query.where(Bookmark.collection_name == collection_name)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_collections(self, user_id: int) -> list[tuple[str, int]]:
        result = await self.db.execute(
            select(Bookmark.collection_name, func.count(Bookmark.id))
            .where(Bookmark.user_id == user_id)
            .group_by(Bookmark.collection_name)
        )
        return list(result.all())

    async def create(self, user_id: int, issue_id: int, collection_name: str, note: str | None) -> Bookmark:
        bookmark = Bookmark(user_id=user_id, issue_id=issue_id, collection_name=collection_name, note=note)
        self.db.add(bookmark)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            raise ValueError("This issue is already bookmarked.")
        return await self.get_by_id(bookmark.id)

    async def delete(self, bookmark: Bookmark) -> None:
        await self.db.delete(bookmark)
        await self.db.commit()
