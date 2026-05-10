import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.comment_service import CommentService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/articles/{article_id}/comments", tags=["comments"])

@router.post("/", response_model=CommentResponse, status_code=201)
async def create_comment(
    article_id: uuid.UUID,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommentService(db)
    return await service.create_comment(article_id, data.text, current_user)

@router.get("/", response_model=dict)
async def list_comments(
    article_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = CommentService(db)
    return await service.get_comments(article_id, page, size)

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    article_id: uuid.UUID,
    comment_id: uuid.UUID,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommentService(db)
    return await service.update_comment(comment_id, data.text, current_user)

@router.delete("/{comment_id}", status_code=204)
async def delete_comment(
    article_id: uuid.UUID,
    comment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = CommentService(db)
    await service.delete_comment(comment_id, current_user)