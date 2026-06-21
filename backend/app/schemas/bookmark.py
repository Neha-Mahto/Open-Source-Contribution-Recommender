from datetime import datetime

from pydantic import BaseModel


class BookmarkCreate(BaseModel):
    issue_id: int
    collection_name: str = "Default"
    note: str | None = None


class BookmarkOut(BaseModel):
    id: int
    issue_id: int
    collection_name: str
    note: str | None
    created_at: datetime
    # Denormalized fields from the related Issue/Repository, filled in by the route --
    # not a 1:1 ORM mapping, so this schema is built manually rather than via from_attributes.
    issue_title: str | None = None
    issue_url: str | None = None
    repository_full_name: str | None = None


class CollectionSummary(BaseModel):
    collection_name: str
    count: int
