from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .schemas import UserCreate,UserResponse
from .database import get_db
from .models import User
from .utils import hash_password

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session=Depends(get_db)):
    existing_user = db.query(User).filter(User.email==user.email).first()
    if existing_user:
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