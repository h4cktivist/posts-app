from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.db import models
from app.schemas.post import PostCreate

logger = get_logger("db")


class PostsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, post_id: int) -> models.Post | None:
        logger.info(f"DB GET post {post_id}")
        result = await self.db.execute(
            select(models.Post).where(models.Post.id == post_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: PostCreate) -> models.Post:
        logger.info("DB CREATE post")
        post = models.Post(**data.model_dump())
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post_id: int, data: PostCreate) -> models.Post | None:
        post = await self.get(post_id)
        if not post:
            return None

        for k, v in data.model_dump().items():
            setattr(post, k, v)

        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: int) -> models.Post | None:
        post = await self.get(post_id)
        if not post:
            return None

        await self.db.delete(post)
        await self.db.commit()
        return post
