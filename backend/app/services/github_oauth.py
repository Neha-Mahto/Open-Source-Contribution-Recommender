"""
Handles the GitHub OAuth handshake.

Flow:
  1. build_authorize_url()  -> frontend redirects user here
  2. GitHub redirects back to our callback with a `code`
  3. exchange_code_for_token(code) -> GitHub access token
  4. fetch_github_profile(token)   -> the user's GitHub profile
"""

import httpx

from app.config import settings

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_CALLBACK_URL,
        "scope": "read:user user:email repo",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GITHUB_AUTHORIZE_URL}?{query}"


async def exchange_code_for_token(code: str) -> str:
    """Exchanges the temporary `code` GitHub gave us for a real access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_CALLBACK_URL,
            },
        )
        response.raise_for_status()
        data = response.json()

    if "access_token" not in data:
        raise ValueError(f"GitHub OAuth exchange failed: {data}")

    return data["access_token"]


async def fetch_github_profile(access_token: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
    }
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(f"{settings.GITHUB_API_BASE_URL}/user", headers=headers)
        user_resp.raise_for_status()
        profile = user_resp.json()

        # Email is often null on /user if it's private -- fetch it separately.
        if not profile.get("email"):
            emails_resp = await client.get(f"{settings.GITHUB_API_BASE_URL}/user/emails", headers=headers)
            if emails_resp.status_code == 200:
                emails = emails_resp.json()
                primary = next((e["email"] for e in emails if e.get("primary")), None)
                profile["email"] = primary

    return profile
