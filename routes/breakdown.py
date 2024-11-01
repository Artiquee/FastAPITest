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


@router.get("/breakdown/", response_model=List[dict])
async def breakdown(
    date_from: str,
    date_to: str,
    db: Session = Depends(get_db)
):
    # Validate date format
    try:
        start_date = datetime.strptime(date_from, "%Y-%m-%d")
        end_date = datetime.strptime(date_to, "%Y-%m-%d")
        print(start_date, end_date)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

    # Fetch comments within the date range
    results = (
        db.query(
            Comment.created_at,
            Comment.is_blocked,
        )
        .filter(Comment.created_at >= start_date, Comment.created_at <= end_date)
        .all()
    )
    print(results)
    # Process the results to create a daily summary
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