from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import get_logger
from app.core.redis import redis_client
from app.db import models
from app.db.session import get_db
from app.repositories.posts_cache_repository import PostsCacheRepository
from app.repositories.posts_repository import PostsRepository
from app.schemas.post import PostCreate, PostResponse

logger = get_logger("service")


class PostsService:
    def __init__(
        self,
        db_repo: PostsRepository,
        cache_repo: PostsCacheRepository,
    ) -> None:
        self.db_repo = db_repo
        self.cache_repo = cache_repo

    async def get_post(self, post_id: int) -> PostResponse | None:
        cached = await self.cache_repo.get(post_id)
        if cached:
            return cached

        post = await self.db_repo.get(post_id)
        if not post:
            logger.warning(f"Post {post_id} not found")
            return None

        response = PostResponse.model_validate(post)
        await self.cache_repo.set(response)
        return response

    async def create_post(self, data: PostCreate) -> models.Post:
        return await self.db_repo.create(data)

    async def update_post(
        self, post_id: int, data: PostCreate
    ) -> models.Post | None:
        post = await self.db_repo.update(post_id, data)
        if post:
            await self.cache_repo.delete(post_id)
        return post

    async def delete_post(self, post_id: int) -> models.Post | None:
        post = await self.db_repo.delete(post_id)
        if post:
            await self.cache_repo.delete(post_id)
        return post


async def get_service(db: AsyncSession = Depends(get_db)) -> PostsService:
    return PostsService(
        PostsRepository(db),
        PostsCacheRepository(redis_client, settings.cache_ttl)
    )
