from fastapi import APIRouter, Depends, HTTPException

from app.core.logger import get_logger
from app.schemas.post import PostCreate, PostResponse
from app.services.posts_service import PostsService, get_service

router = APIRouter()
logger = get_logger("api.posts")


@router.get("/posts/{post_id}")
async def get_post(
    post_id: int, service: PostsService = Depends(get_service)
) -> PostResponse:
    try:
        post = await service.get_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get post: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to retrieve post"
        ) from exc


@router.post("/posts")
async def create_post(
    data: PostCreate, service: PostsService = Depends(get_service)
) -> PostResponse:
    try:
        created = await service.create_post(data)
        return PostResponse.model_validate(created)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create post: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to create post"
        ) from exc


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int, data: PostCreate, service: PostsService = Depends(get_service)
) -> PostResponse:
    try:
        post = await service.update_post(post_id, data)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostResponse.model_validate(post)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to update post: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to update post"
        ) from exc


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int, service: PostsService = Depends(get_service)
) -> dict[str, bool]:
    try:
        post = await service.delete_post(post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to delete post: %s", exc)
        raise HTTPException(
            status_code=500, detail="Failed to delete post"
        ) from exc
