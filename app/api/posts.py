from fastapi import APIRouter, Depends, HTTPException

from app.core.logger import get_logger
from app.schemas.post import PostCreate
from app.services.posts_service import PostsService, get_service

router = APIRouter()
logger = get_logger("api.posts")


@router.get("/posts/{post_id}")
async def get_post(post_id: int, service: PostsService = Depends(get_service)):
    try:
        post = await service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404)
        return post
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to get post %s", post_id)
        raise HTTPException(status_code=500)


@router.post("/posts")
async def create_post(data: PostCreate, service: PostsService = Depends(get_service)):
    try:
        return await service.create_post(data)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to create post")
        raise HTTPException(status_code=500)


@router.put("/posts/{post_id}")
async def update_post(post_id: int, data: PostCreate, service: PostsService = Depends(get_service)):
    try:
        post = await service.update_post(post_id, data)
        if not post:
            raise HTTPException(status_code=404)
        return post
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to update post %s", post_id)
        raise HTTPException(status_code=500)


@router.delete("/posts/{post_id}")
async def delete_post(post_id: int, service: PostsService = Depends(get_service)):
    try:
        post = await service.delete_post(post_id)
        if not post:
            raise HTTPException(status_code=404)
        return {"ok": True}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to delete post %s", post_id)
        raise HTTPException(status_code=500)
