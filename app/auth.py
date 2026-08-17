from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import UserCreate, UserResponse, UserLogin
from .database import get_db
from .models import User
from .utils import hash_password, verify_password
from .security import create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session=Depends(get_db)):
    existing_email = db.query(User).filter(User.email==user.email).first()
    if existing_email:
        raise HTTPException(status_code=409, detail="email already registered")
    existing_username = db.query(User).filter(User.username==user.username).first()
    if existing_username:
        raise HTTPException(status_code=409,detail="username already taken")

    hashed_password = hash_password(user.password)
    new_user = User(username = user.username,
                    email = user.email,
                    password = hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/auth/login")
def login(login_data: UserLogin, db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.email == login_data.email).first()
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(login_data.password, db_user.password):
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
@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user