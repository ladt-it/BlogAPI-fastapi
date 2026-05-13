import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse, ArticleListResponse
from app.services.article_service import ArticleService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/articles", tags=["articles"])

@router.post("/", response_model=ArticleResponse, status_code=201)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    return await service.create_article(data, current_user)

@router.get("/", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    author_id: uuid.UUID | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    return await service.list_articles(page, size, author_id, search)

@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    service = ArticleService(db)
    return await service.get_article(article_id)

@router.put("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: uuid.UUID,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    return await service.update_article(article_id, data, current_user)

@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ArticleService(db)
    await service.delete_article(article_id, current_user)