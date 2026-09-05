from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .schemas import PostCreate, PostResponse, PostDetailResponse
from .database import get_db
from .models import Post, User
from .security import get_current_user
from enum import Enum


class SortOrder(str, Enum):
    latest = "latest"
    oldest = "oldest"


router = APIRouter(tags=["Posts"])


@router.post(
    "/posts",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    description="Create a new blog post for the currently authenticated user."
)
def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get(
    "/posts",
    response_model=list[PostResponse],
    summary="Get all posts",
    description="Return a paginated list of blog posts with optional title filtering and sorting."
)
def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: str | None = None,
    sort: SortOrder = SortOrder.latest,
    db: Session = Depends(get_db)
):
    query = db.query(Post)

    if title:
        query = query.filter(Post.title.ilike(f"%{title}%"))

    if sort == SortOrder.latest:
        query = query.order_by(Post.created_at.desc())
    elif sort == SortOrder.oldest:
        query = query.order_by(Post.created_at.asc())

    posts = query.offset(skip).limit(limit).all()

    return posts


@router.get(
    "/posts/{post_id}",
    response_model=PostDetailResponse,
    summary="Get a post",
    description="Return a single blog post along with its details."
)
def get_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    post = db.query(Post).filter(Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=404,
            detail="Post not found"
        )

    return post


@router.put(
    "/posts/{post_id}",
    response_model=PostResponse,
    summary="Update a post",
    description="Update a blog post. Only the post owner can update it."
)
def update_post(
    post_id: int,
    post: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing_post = db.query(Post).filter(Post.id == post_id).first()

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


@router.delete(
    "/posts/{post_id}",
    summary="Delete a post",
    description="Delete a blog post. Only the post owner can delete it."
)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    return {"message": "Post deleted successfully"}