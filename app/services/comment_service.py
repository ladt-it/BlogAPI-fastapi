import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.comment_repo import CommentRepository
from app.repositories.article_repo import ArticleRepository
from app.models.user import User

class CommentService:
    def __init__(self, db: AsyncSession):
        self.comment_repo = CommentRepository(db)
        self.article_repo = ArticleRepository(db)

    async def create_comment(self, article_id: uuid.UUID, text: str, current_user: User) -> dict:
        # Проверим, что статья существует
        article = await self.article_repo.get_by_id(article_id)
        if not article:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Article not found")
        comment = await self.comment_repo.create(text=text, article_id=article_id, user_id=current_user.id)
        return self._to_dict(comment)

    async def get_comments(self, article_id: uuid.UUID, page: int, size: int) -> dict:
        comments, total = await self.comment_repo.list_for_article(article_id, page, size)
        return {
            "items": [self._to_dict(c) for c in comments],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }

    async def update_comment(self, comment_id: uuid.UUID, text: str, current_user: User) -> dict:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        updated = await self.comment_repo.update(comment, text)
        return self._to_dict(updated)

    async def delete_comment(self, comment_id: uuid.UUID, current_user: User) -> None:
        comment = await self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
        if comment.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your comment")
        await self.comment_repo.delete(comment)

    def _to_dict(self, comment) -> dict:
        return {
            "id": str(comment.id),
            "text": comment.text,
            "article_id": str(comment.article_id),
            "user_id": str(comment.user_id),
            "created_at": comment.created_at,
        }