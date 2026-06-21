"""
Auth flow:

  GET  /auth/github/login     -> redirects browser to GitHub's consent screen
  GET  /auth/github/callback  -> GitHub redirects here with ?code=...&state=...
                                  we exchange the code, upsert the user, and
                                  redirect to the frontend with OUR jwt token
  GET  /auth/me               -> returns the logged-in user's profile
"""

import secrets

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.deps import get_current_user
from app.core.security import create_access_token
from app.database import get_db
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserOut
from app.services import github_oauth
from app.services.redis_client import redis_client

router = APIRouter(prefix="/auth", tags=["auth"])

STATE_TTL_SECONDS = 600  # 10 minutes to complete the login flow


@router.get("/github/login")
async def github_login():
    """Step 1: send the user to GitHub's consent screen."""
    state = secrets.token_urlsafe(24)
    # Store state in Redis so the callback can verify this request wasn't forged.
    await redis_client.set(f"oauth_state:{state}", "1", ex=STATE_TTL_SECONDS)

    authorize_url = github_oauth.build_authorize_url(state=state)
    return RedirectResponse(authorize_url)


@router.get("/github/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Step 2: GitHub redirects back here after the user approves access."""
    state_key = f"oauth_state:{state}"
    state_exists = await redis_client.get(state_key)
    if not state_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired OAuth state")
    await redis_client.delete(state_key)

    try:
        github_token = await github_oauth.exchange_code_for_token(code)
        profile = await github_oauth.fetch_github_profile(github_token)
    except (ValueError, httpx.HTTPStatusError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"GitHub login failed: {exc}")

    user = await UserRepository(db).upsert_from_github_profile(
        github_id=profile["id"],
        github_username=profile["login"],
        avatar_url=profile.get("avatar_url"),
        name=profile.get("name"),
        email=profile.get("email"),
        access_token=github_token,
    )

    our_jwt = create_access_token(user_id=user.id)

    # Hand the token to the frontend via a redirect with a query param.
    # The SPA reads it from the URL once, then stores it in memory/local state.
    redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={our_jwt}"
    return RedirectResponse(redirect_url)


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
