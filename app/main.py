from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.posts import router
from app.core.logger import setup_logger, get_logger
from app.db.session import init_db

setup_logger()
logger = get_logger("api")


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
