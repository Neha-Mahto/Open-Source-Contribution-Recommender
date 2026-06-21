"""
Thin wrapper around the GitHub REST API for repo/issue data (separate from
github_oauth.py, which only handles the login handshake).

Every read goes through Redis first (cache-aside pattern). On a cache miss
we hit GitHub, store the result with a short TTL, and return it. This is
what keeps the app from blowing through GitHub's rate limit -- 60 requests/hr
unauthenticated, 5000/hr authenticated -- the moment more than a couple of
users are browsing repos at once.
"""

import json
from datetime import datetime

import httpx

from app.config import settings
from app.services.redis_client import redis_client

REPO_CACHE_TTL_SECONDS = 600     # 10 min -- repo metadata changes slowly
ISSUES_CACHE_TTL_SECONDS = 180   # 3 min -- issues change more often


class GitHubRateLimitError(Exception):
    """Raised when GitHub's API rate limit is exhausted, instead of letting a raw 403 bubble up."""

    def __init__(self, reset_at: datetime | None = None):
        self.reset_at = reset_at
        super().__init__(f"GitHub API rate limit exceeded. Resets at {reset_at}")


def _auth_headers(access_token: str | None) -> dict:
    headers = {"Accept": "application/vnd.github+json"}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _check_rate_limit(response: httpx.Response) -> None:
    """Convert an exhausted-rate-limit response into a typed exception the route layer can catch."""
    remaining = response.headers.get("X-RateLimit-Remaining")
    if response.status_code in (403, 429) and remaining == "0":
        reset_header = response.headers.get("X-RateLimit-Reset")
        reset_at = datetime.fromtimestamp(int(reset_header)) if reset_header else None
        raise GitHubRateLimitError(reset_at=reset_at)


async def get_repository(full_name: str, access_token: str | None = None, force_refresh: bool = False) -> dict:
    """Fetch a single repo's metadata. Cached in Redis under gh:repo:{full_name}."""
    cache_key = f"gh:repo:{full_name}"

    if not force_refresh:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.GITHUB_API_BASE_URL}/repos/{full_name}",
            headers=_auth_headers(access_token),
        )

    _check_rate_limit(response)
    response.raise_for_status()
    data = response.json()

    await redis_client.set(cache_key, json.dumps(data), ex=REPO_CACHE_TTL_SECONDS)
    return data


async def list_repository_issues(
    full_name: str,
    access_token: str | None = None,
    state: str = "open",
    page: int = 1,
    per_page: int = 50,
    force_refresh: bool = False,
) -> list[dict]:
    """
    Fetch a page of issues for a repo. Cached in Redis.

    Note: GitHub's /issues endpoint also returns pull requests mixed in --
    callers should filter on `"pull_request" not in item` if they only
    want real issues (the sync service does this).
    """
    cache_key = f"gh:issues:{full_name}:{state}:{page}:{per_page}"

    if not force_refresh:
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.GITHUB_API_BASE_URL}/repos/{full_name}/issues",
            headers=_auth_headers(access_token),
            params={"state": state, "page": page, "per_page": per_page},
        )

    _check_rate_limit(response)
    response.raise_for_status()
    data = response.json()

    await redis_client.set(cache_key, json.dumps(data), ex=ISSUES_CACHE_TTL_SECONDS)
    return data


async def get_rate_limit_status(access_token: str | None = None) -> dict:
    """Lets the frontend show 'X requests remaining' instead of users hitting a wall blind."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.GITHUB_API_BASE_URL}/rate_limit",
            headers=_auth_headers(access_token),
        )
    response.raise_for_status()
    return response.json()
