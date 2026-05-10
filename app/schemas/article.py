from datetime import datetime
from pydantic import BaseModel

class ArticleCreate(BaseModel):
    title: str
    content: str

class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    size: int
    pages: int