from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.redis import redis_client
from app.core.config import settings
from app.db.session import get_db
from app.repositories.posts_repository import PostsRepository
from app.repositories.posts_cache_repository import PostsCacheRepository

logger = get_logger("service")


class PostsService:
    def __init__(self, db_repo, cache_repo):
        self.db_repo = db_repo
        self.cache_repo = cache_repo

    async def get_post(self, post_id: int):
        cached = await self.cache_repo.get(post_id)
        if cached:
            return cached

        post = self.db_repo.get(post_id)
        if not post:
            logger.warning(f"Post {post_id} not found")
            return None

        post_dict = {
            "id": post.id,
            "title": post.title,
            "content": post.content
        }

        await self.cache_repo.set(post_dict)
        return post_dict

    async def create_post(self, data):
        return self.db_repo.create(data)

    async def update_post(self, post_id: int, data):
        post = self.db_repo.update(post_id, data)
        if post:
            await self.cache_repo.delete(post_id)
        return post

    async def delete_post(self, post_id: int):
        post = self.db_repo.delete(post_id)
        if post:
            await self.cache_repo.delete(post_id)
        return post


def get_service(db: Session = Depends(get_db)):
    return PostsService(
        PostsRepository(db),
        PostsCacheRepository(redis_client, settings.cache_ttl)
    )
