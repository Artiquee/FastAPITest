import time
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.orm import Session
from db.db_settings import get_db
from db.models.comment import Comment
from db.models.post import Post
from db.models.user import User
from schemas.comment_schema import CommentCreate, CommentUpdate, ResponseStatus, DailyCommentSummary
from utils.auth import get_current_active_user

router = APIRouter()


@router.get("/comments/", response_model=List[ResponseStatus])
async def read_comments(post_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    result = db.query(Comment).filter(Comment.post_id == post_id, Comment.author_id == current_user.id).offset(skip).limit(limit)
    comments = result.all()
    return [{"status": "success", "data": comment} for comment in comments]


@router.get("/comments/{comment_id}", response_model=ResponseStatus)
async def read_comment(comment_id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_active_user)):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == current_user.id).first()
    return {"status": "success", "data": comment}


@router.post("/comments/", response_model=ResponseStatus, status_code=status.HTTP_201_CREATED)
async def create_comment(
    comment: CommentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_post = db.query(Post).filter(Post.id == comment.post_id).first()
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    new_comment = Comment(**comment.dict(), author_id=current_user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    if db_post.autoreply:
        background_tasks.add_task(create_autoreply_comment, db_post.id, db)

    return {"status": "success", "data": new_comment}


@router.put("/comments/{comment_id}", response_model=ResponseStatus)
async def update_comment(comment_id: int, comment: CommentUpdate, post_id: int = Query(...),
                         author_id: int = Query(...), db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.post_id == post_id,
        Comment.author_id == author_id,
        Comment.author_id == current_user.id
    ).first()

    if db_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    for key, value in comment.dict(exclude_unset=True).items():
        setattr(db_comment, key, value)

    db.commit()
    db.refresh(db_comment)
    return {"status": "success", "data": db_comment}


@router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_active_user)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id, Comment.author_id == current_user.id).first()
    db.delete(db_comment)
    db.commit()
    return {"status": "success", "detail": "Comment deleted successfully"}


def create_autoreply_comment(post_id: int, db: Session):
    db_post = db.query(Post).filter(Post.id == post_id).first()

    if not db_post:
        return

    autoreply_comment = Comment(content=db_post.autoreply_msg, post_id=post_id, author_id=db_post.owner_id)
    time.sleep(db_post.autoreply_delay)
    db.add(autoreply_comment)
    db.commit()
    db.refresh(autoreply_comment)
    print(f"Автоматична відповідь створена для поста ID {post_id}: {db_post.autoreply_msg}")


@router.get("/breakdown/", response_model=List[dict])
async def breakdown(
    date_from: str,
    date_to: str,
    db: Session = Depends(get_db)
):
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        print(start_date, end_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

    results = (
        db.query(
            Comment.created_at,
            Comment.is_blocked,
        )
        .filter(Comment.created_at >= start_date, Comment.created_at <= end_date)
        .all()
    )
    daily_summary = {}

    for created_at, is_blocked in results:
        day = created_at.date()
        if day not in daily_summary:
            daily_summary[day] = {"total_comments": 0, "blocked_comments": 0}

        daily_summary[day]["total_comments"] += 1
        if is_blocked:
            daily_summary[day]["blocked_comments"] += 1

    # Format the response
    return [
        {
            "date": str(day),
            "total_comments": data["total_comments"],
            "blocked_comments": data["blocked_comments"]
        }
        for day, data in daily_summary.items()
    ]
