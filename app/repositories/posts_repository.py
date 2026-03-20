from sqlalchemy.orm import Session
from app.db import models
from app.core.logger import get_logger


logger = get_logger("db")


class PostsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, post_id: int):
        logger.info(f"DB GET post {post_id}")
        return self.db.query(models.Post).filter(models.Post.id == post_id).first()

    def create(self, data):
        logger.info("DB CREATE post")
        post = models.Post(**data.model_dump())
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def update(self, post_id: int, data):
        post = self.get(post_id)
        if not post:
            return None

        for k, v in data.model_dump().items():
            setattr(post, k, v)

        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post_id: int):
        post = self.get(post_id)
        if not post:
            return None

        self.db.delete(post)
        self.db.commit()
        return post
