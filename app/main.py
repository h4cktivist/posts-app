from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.posts import router
from app.core.logger import setup_logger, get_logger
from app.core.redis import close_redis, init_redis
from app.db.session import close_db, init_db

setup_logger()
logger = get_logger("api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        await init_db()
        logger.info("Database setup complete")
    except Exception:
        logger.exception("Database setup failed")
        raise
    try:
        await init_redis()
        logger.info("Redis setup complete")
    except Exception:
        logger.exception("Redis setup failed")
        raise
    yield
    await close_redis()
    await close_db()


app = FastAPI(lifespan=lifespan)
app.include_router(router)
