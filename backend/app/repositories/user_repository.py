"""
Data-access layer for the User model.

Routes/services should never write raw SQLAlchemy queries directly against
session -- they go through a Repository class like this one. It keeps query
logic in one place and makes services easy to unit test with a fake repo.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_github_id(self, github_id: int) -> User | None:
        result = await self.db.execute(select(User).where(User.github_id == github_id))
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def upsert_from_github_profile(
        self,
        github_id: int,
        github_username: str,
        avatar_url: str | None,
        name: str | None,
        email: str | None,
        access_token: str,
    ) -> User:
        """Create the user on first login, or refresh their profile on every later login."""
        existing = await self.get_by_github_id(github_id)
        if existing:
            return await self.update(
                existing,
                github_username=github_username,
                avatar_url=avatar_url,
                name=name,
                email=email,
                github_access_token=access_token,
            )
        return await self.create(
            github_id=github_id,
            github_username=github_username,
            avatar_url=avatar_url,
            name=name,
            email=email,
            github_access_token=access_token,
        )
