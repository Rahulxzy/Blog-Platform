from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .schemas import PostCreate, PostResponse
from .database import get_db
from .models import Post, User
from .security import get_current_user

router = APIRouter()

@router.post("/posts", response_model=PostResponse)
def create_post(post:PostCreate, current_user: User=Depends(get_current_user),db: Session=Depends(get_db)):
    new_post = Post(title=post.title, content=post.content, user_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/posts", response_model=list[PostResponse])
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    return posts

@router.get("/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    return post

@router.put("/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post: PostCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_post = (db.query(Post).filter(Post.id == post_id).first())
    if not existing_post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to update this post"
        )

    existing_post.title = post.title
    existing_post.content = post.content

    db.commit()
    db.refresh(existing_post)
    return existing_post

@router.delete("/posts/{post_id}")
def delete_post(post_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing_post = db.query(Post).filter(Post.id == post_id).first()
    if not existing_post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )
    if existing_post.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this post"
        )
    db.delete(existing_post)
    db.commit()
    return {"message":"Post deleted successfully"}