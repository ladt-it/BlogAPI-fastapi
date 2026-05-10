import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment

class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, text: str, article_id: uuid.UUID, user_id: uuid.UUID) -> Comment:
        comment = Comment(text=text, article_id=article_id, user_id=user_id)
        self.db.add(comment)
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: uuid.UUID) -> Comment | None:
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def list_for_article(self, article_id: uuid.UUID, page: int = 1, size: int = 20) -> tuple[list[Comment], int]:
        query = select(Comment).where(Comment.article_id == article_id).order_by(Comment.created_at.desc())
        count_query = select(func.count(Comment.id)).where(Comment.article_id == article_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        query = query.offset((page - 1) * size).limit(size)
        result = await self.db.execute(query)
        comments = result.scalars().all()

        return list(comments), total

    async def update(self, comment: Comment, text: str) -> Comment:
        comment.text = text
        await self.db.commit()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.commit()