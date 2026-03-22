import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Post
from app.db.session import Base
from app.repositories.posts_cache_repository import PostsCacheRepository
from app.repositories.posts_repository import PostsRepository
from app.schemas.post import PostCreate, PostResponse
from app.services.posts_service import PostsService


class InMemoryAsyncRedis:
    def __init__(self):
        self.storage = {}
        self.ttl_by_key = {}

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.storage[key] = value
        self.ttl_by_key[key] = ex

    async def delete(self, key: str):
        self.storage.pop(key, None)
        self.ttl_by_key.pop(key, None)


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    session = factory()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def service(db_session: AsyncSession):
    redis = InMemoryAsyncRedis()
    cache_repo = PostsCacheRepository(redis=redis, ttl=60)
    db_repo = PostsRepository(db_session)
    return PostsService(db_repo=db_repo, cache_repo=cache_repo)


async def _create_post(
    db_session: AsyncSession, title: str = "title", content: str = "content"
) -> Post:
    post = Post(title=title, content=content)
    db_session.add(post)
    await db_session.commit()
    await db_session.refresh(post)
    return post


@pytest.mark.anyio
async def test_get_post_uses_cache_after_first_db_read(
    service: PostsService, db_session: AsyncSession
):
    post = await _create_post(db_session, title="first", content="from-db")

    first_read = await service.get_post(post.id)
    assert first_read == PostResponse(
        id=post.id, title="first", content="from-db"
    )

    await db_session.delete(post)
    await db_session.commit()

    second_read = await service.get_post(post.id)
    assert second_read == PostResponse(
        id=post.id, title="first", content="from-db"
    )


@pytest.mark.anyio
async def test_update_post_invalidates_cache(
    service: PostsService, db_session: AsyncSession
):
    post = await _create_post(db_session, title="old-title", content="old-content")
    await service.get_post(post.id)

    await service.update_post(
        post.id, PostCreate(title="new-title", content="new-content")
    )

    cached_after_update = await service.cache_repo.get(post.id)
    assert cached_after_update is None

    refreshed = await service.get_post(post.id)
    assert refreshed == PostResponse(
        id=post.id, title="new-title", content="new-content"
    )


@pytest.mark.anyio
async def test_delete_post_invalidates_cache(
    service: PostsService, db_session: AsyncSession
):
    post = await _create_post(db_session, title="to-delete", content="to-delete")
    await service.get_post(post.id)

    await service.delete_post(post.id)

    cached_after_delete = await service.cache_repo.get(post.id)
    assert cached_after_delete is None

    missing = await service.get_post(post.id)
    assert missing is None
