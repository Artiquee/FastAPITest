from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.models.post import Post
from db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.post_schema import PostCreate, PostUpdate, PostScheme
from db.db_settings import get_db
from utils.auth import get_current_active_user

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=List[PostScheme])
async def read_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    posts = db.query(Post).filter(Post.owner_id == current_user.id).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=PostScheme)
async def read_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    post = db.query(Post).filter((Post.owner_id == current_user.id) & (Post.id == post_id)).first()
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/", response_model=PostScheme, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    post = Post(**post.dict(), owner_id=current_user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


@router.put("/{post_id}", response_model=PostScheme, status_code=status.HTTP_200_OK)
async def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == current_user.id).first()
    if db_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)

    db.commit()
    db.refresh(db_post)
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    db_post = db.query(Post).filter(Post.id == post_id, Post.owner_id == current_user.id).first()  # Змінено
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")  # Змінено
    db.delete(db_post)
    db.commit()
    return {"detail": "Post deleted successfully"}


async def get_post_or_404(db: AsyncSession, post_id: int, user_id: int) -> Post:
    result = await db.execute(select(Post).filter(Post.id == post_id, Post.owner_id == user_id))
    post = result.scalars().first()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post
