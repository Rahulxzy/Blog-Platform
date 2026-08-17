from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import CommentCreate, CommentResponse
from .database import get_db
from .models import Comment, User, Post
from .security import get_current_user

router = APIRouter()

@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def create_comment(post_id: int, comment: CommentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_post = (db.query(Post).filter(Post.id == post_id).first())
    if not existing_post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    new_comment = Comment(
        content = comment.content,
        user_id = current_user.id,
        post_id = post_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/posts/{post_id}/comments", response_model=list[CommentResponse])
def get_comments(post_id: int, db: Session = Depends(get_db)):
    existing_post = (db.query(Post).filter(Post.id == post_id).first())
    if not existing_post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    comments = (db.query(Comment).filter(Comment.post_id == post_id).all())

    return comments

@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_comment = (db.query(Comment).filter(Comment.id == comment_id).first())
    if not existing_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this comment"
        )

    existing_comment.content = comment.content
    db.commit()
    db.refresh(existing_comment)
    return existing_comment

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_comment = (db.query(Comment).filter(Comment.id == comment_id).first())
    if not existing_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found"
        )

    if existing_comment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this comment"
        )

    db.delete(existing_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}