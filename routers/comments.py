from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from sqlalchemy.orm import Session
from database import get_db
import schemas
import models
from oauth2 import get_current_user

router = APIRouter(prefix="/blog", tags=["Comments"])


@router.post("/{blog_id}/comment", status_code=status.HTTP_201_CREATED)
def create_comment(
    blog_id: int,
    request: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found",
        )
    comment = models.Comment(
        text=request.text, user_id=logedIn_user.id, blog_id=blog.id
    )
    if blog.user_id != logedIn_user.id:
        db.add(comment)
        db.commit()
        db.refresh(comment)
        return comment
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot comment on your own blog post",
        )


@router.get(
    "/{blog_id}/comments",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Comment],
)
def get_comments_for_blog(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Blog with id {blog_id} not found",
        )
    return blog.comments


@router.delete("/{comment_id}/comment/delete", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user),
):
    logedIn_user = (
        db.query(models.User).filter(models.User.email == current_user.email).first()
    )
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found",
        )

    blog = db.query(models.Blog).filter(models.Blog.id == comment.blog_id).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Associated blog for comment with id {comment_id} not found",
        )

    if blog.user_id == logedIn_user.id:
        db.delete(comment)
        db.commit()
        return {"details": "Comment deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this comment",
        )
