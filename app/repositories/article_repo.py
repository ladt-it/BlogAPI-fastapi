import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.article import Article

class ArticleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, title: str, content: str, author_id: uuid.UUID) -> Article:
        article = Article(title=title, content=content, author_id=author_id)
        self.db.add(article)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def get_by_id(self, article_id: uuid.UUID) -> Article | None:
        result = await self.db.execute(select(Article).where(Article.id == article_id))
        return result.scalar_one_or_none()

    async def list_with_pagination(
        self, page: int = 1, size: int = 10, author_id: uuid.UUID | None = None,
        search: str | None = None
    ) -> tuple[list[Article], int]:
        query = select(Article)
        count_query = select(func.count(Article.id))

        if author_id:
            query = query.where(Article.author_id == author_id)
            count_query = count_query.where(Article.author_id == author_id)
        if search:
            query = query.where(Article.title.ilike(f"%{search}%"))
            count_query = count_query.where(Article.title.ilike(f"%{search}%"))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(Article.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        articles = result.scalars().all()

        return list(articles), total

    async def update(self, article: Article, **kwargs) -> Article:
        for key, value in kwargs.items():
            if value is not None:
                setattr(article, key, value)
        await self.db.commit()
        await self.db.refresh(article)
        return article

    async def delete(self, article: Article) -> None:
        await self.db.delete(article)
        await self.db.commit()