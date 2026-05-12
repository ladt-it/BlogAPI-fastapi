import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.article_repo import ArticleRepository
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.core.redis_client import RedisClient


class ArticleService:
    def __init__(self, db: AsyncSession):
        self.article_repo = ArticleRepository(db)
        self.redis = RedisClient()

    async def create_article(self, data: ArticleCreate, current_user: User) -> dict:
        article = await self.article_repo.create(
            title=data.title,
            content=data.content,
            author_id=current_user.id,
        )
        await self.redis.delete_pattern("articles:list:*")  # ← сбрасываем весь кэш статей
        return self._to_dict(article)

    async def get_article(self, article_id: uuid.UUID) -> dict:
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        return self._to_dict(article)

    async def list_articles(self, page: int, size: int, author_id: uuid.UUID | None, search: str | None) -> dict:
        cache_key = f"articles:list:{page}:{size}:{author_id}:{search}"
        cached = await self.redis.get(cache_key)
        if cached:
            return cached

        articles, total = await self.article_repo.list_with_pagination(page, size, author_id, search)
        # Убедимся, что каждый элемент сериализован
        items = [self._to_dict(a) for a in articles]
        result = {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }
        await self.redis.set(cache_key, result, ttl=30)
        return result

        # Сохраняем в кэш на 30 секунд
        await self.redis.set(cache_key, result, ttl=30)
        return result

    async def update_article(
        self, article_id: uuid.UUID, data: ArticleUpdate, current_user: User
    ) -> dict:
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        if article.author_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your article")
        updated = await self.article_repo.update(
            article, title=data.title, content=data.content
        )
        await self.redis.delete_pattern("articles:list:*")  # ←
        return self._to_dict(updated)

    async def delete_article(self, article_id: uuid.UUID, current_user: User) -> None:
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        if article.author_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your article")
        await self.article_repo.delete(article)
        await self.redis.delete_pattern("articles:list:*")

    def _to_dict(self, article) -> dict:
        return {
            "id": str(article.id),
            "title": article.title,
            "content": article.content,
            "author_id": str(article.author_id),
            "created_at": str(article.created_at),
            "updated_at": str(article.updated_at),
        }