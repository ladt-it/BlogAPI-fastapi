from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.routers import auth, articles, comments

app = FastAPI(title="Blog API")

app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(comments.router)


@app.get("/")
async def root():
    return {"message": "Blog API is running"}


@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}