"""
Bookmark endpoints -- saving issues into named collections
(e.g. "Hacktoberfest Targets", "Backend Projects").

  POST   /bookmarks              Save an issue
  GET    /bookmarks              List the current user's saved issues
  GET    /bookmarks/collections  List collection names with counts
  DELETE /bookmarks/{id}         Remove a saved issue
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Bookmark, User
from app.repositories.bookmark_repository import BookmarkRepository
from app.schemas.bookmark import BookmarkCreate, BookmarkOut, CollectionSummary

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


def _to_bookmark_out(bookmark: Bookmark) -> BookmarkOut:
    issue = bookmark.issue
    return BookmarkOut(
        id=bookmark.id,
        issue_id=bookmark.issue_id,
        collection_name=bookmark.collection_name,
        note=bookmark.note,
        created_at=bookmark.created_at,
        issue_title=issue.title if issue else None,
        issue_url=issue.url if issue else None,
        repository_full_name=issue.repository.full_name if issue and issue.repository else None,
    )


@router.post("", response_model=BookmarkOut, status_code=status.HTTP_201_CREATED)
async def create_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        bookmark = await BookmarkRepository(db).create(
            user_id=current_user.id,
            issue_id=payload.issue_id,
            collection_name=payload.collection_name,
            note=payload.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    return _to_bookmark_out(bookmark)


@router.get("", response_model=list[BookmarkOut])
async def list_bookmarks(
    collection: str | None = Query(None, description="Filter by collection name"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bookmarks = await BookmarkRepository(db).list_by_user(current_user.id, collection_name=collection)
    return [_to_bookmark_out(b) for b in bookmarks]


@router.get("/collections", response_model=list[CollectionSummary])
async def list_collections(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rows = await BookmarkRepository(db).list_collections(current_user.id)
    return [CollectionSummary(collection_name=name, count=count) for name, count in rows]


@router.delete("/{bookmark_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    repo = BookmarkRepository(db)
    bookmark = await repo.get_by_id(bookmark_id)
    if bookmark is None or bookmark.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bookmark not found")
    await repo.delete(bookmark)
