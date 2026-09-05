from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .schemas import UserCreate, UserResponse
from .database import get_db
from .models import User
from .utils import hash_password, verify_password
from .security import create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

router = APIRouter(tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account using a unique usernmae and email."
)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_email:
        raise HTTPException(
            status_code=409,
            detail="email already registered"
        )

    existing_username = db.query(User).filter(User.username == user.username).first()

    if existing_username:
        raise HTTPException(
            status_code=409,
            detail="username already taken"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

    db.refresh(new_user)

    return new_user


@router.post(
    "/auth/login",
    summary="Login user",
    description="Authentication a user and return a JWT access token"
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(User).filter(User.email == form_data.username).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(
        {
            "sub": str(db_user.id)
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# temporary endpoint
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return the profile of the currently authenticated user."
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user