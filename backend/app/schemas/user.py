from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    github_username: str
    name: str | None
    email: str | None
    avatar_url: str | None
    known_languages: list[str] | None
    created_at: datetime
