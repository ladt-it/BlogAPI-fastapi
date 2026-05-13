from datetime import datetime
from pydantic import BaseModel

class CommentCreate(BaseModel):
    text: str

class CommentUpdate(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: str
    text: str
    article_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True