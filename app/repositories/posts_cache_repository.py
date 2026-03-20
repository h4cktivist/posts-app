import json
from app.core.logger import get_logger

logger = get_logger("cache")


class PostsCacheRepository:
    def __init__(self, redis, ttl: int):
        self.redis = redis
        self.ttl = ttl

    def _key(self, post_id: int):
        return f"post:{post_id}"

    async def get(self, post_id: int):
        data = await self.redis.get(self._key(post_id))
        if data:
            logger.info(f"Cache HIT post {post_id}")
            return json.loads(data)

        logger.info(f"Cache MISS post {post_id}")
        return None

    async def set(self, post):
        logger.info(f"Cache SET post {post['id']}")
        await self.redis.set(self._key(post["id"]), json.dumps(post), ex=self.ttl)

    async def delete(self, post_id: int):
        logger.info(f"Cache DELETE post {post_id}")
        await self.redis.delete(self._key(post_id))
