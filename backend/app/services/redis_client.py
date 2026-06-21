"""
Single shared Redis connection, used for:
  - Short-lived OAuth `state` tokens (CSRF protection during login)
  - Caching GitHub API responses (added in the next phase)
"""

import redis.asyncio as redis

from app.config import settings

redis_client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
