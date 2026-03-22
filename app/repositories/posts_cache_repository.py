from __future__ import annotations

import json
from typing import Any

from app.core.logger import get_logger
from app.schemas.post import PostResponse

logger = get_logger("cache")


class PostsCacheRepository:
    def __init__(self, redis: Any, ttl: int) -> None:
        self.redis = redis
        self.ttl = ttl

    def _key(self, post_id: int) -> str:
        return f"post:{post_id}"

    async def get(self, post_id: int) -> PostResponse | None:
        data = await self.redis.get(self._key(post_id))
        if data:
            logger.info(f"Cache HIT post {post_id}")
            return PostResponse.model_validate(json.loads(data))

        logger.info(f"Cache MISS post {post_id}")
        return None

    async def set(self, post: PostResponse) -> None:
        logger.info(f"Cache SET post {post.id}")
        await self.redis.set(
            self._key(post.id), json.dumps(post.model_dump()), ex=self.ttl
        )

    async def delete(self, post_id: int) -> None:
        logger.info(f"Cache DELETE post {post_id}")
        await self.redis.delete(self._key(post_id))
