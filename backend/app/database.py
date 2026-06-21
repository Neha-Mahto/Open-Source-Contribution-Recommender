"""
Database connection setup.

Uses SQLAlchemy 2.0 async engine with asyncpg. This is the single source
of truth for DB sessions -- every route/service gets its session through
the get_db() dependency below, never by importing the engine directly.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """All ORM models inherit from this."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a DB session and guarantees cleanup."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Create tables on startup.

    This is fine for local development. In production you'd swap this
    for Alembic migrations (alembic/ folder is already scaffolded --
    run `alembic revision --autogenerate` once models stabilize).
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
