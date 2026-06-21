"""
Import every model here so that `Base.metadata.create_all()` (and Alembic's
autogenerate) can discover all tables. If you add a new model file, add its
import here too -- this is a common gotcha that causes "table not found"
errors that are confusing to debug.
"""

from app.models.user import User
from app.models.repository import Repository
from app.models.issue import Issue, IssueDifficulty
from app.models.bookmark import Bookmark
from app.models.contribution import Contribution, ContributionStatus

__all__ = [
    "User",
    "Repository",
    "Issue",
    "IssueDifficulty",
    "Bookmark",
    "Contribution",
    "ContributionStatus",
]
