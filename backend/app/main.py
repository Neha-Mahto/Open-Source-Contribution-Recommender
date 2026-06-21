from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import auth, bookmarks, contributions, dashboard, issues, repositories


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if they don't exist yet.
    # Swap this for Alembic migrations once the schema stabilizes.
    await init_db()
    yield
    # Shutdown: nothing to clean up yet (engine connections are pooled).


app = FastAPI(
    title=settings.APP_NAME,
    description="Discover GitHub issues that match your skills, and track your open-source contribution journey.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(repositories.router)
app.include_router(issues.router)
app.include_router(bookmarks.router)
app.include_router(contributions.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["meta"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
