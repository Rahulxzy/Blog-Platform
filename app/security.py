from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from .database import get_db
from .models import User
from .config import settings


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes = settings.access_token_expire_minutes)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.secret_key,algorithm=settings.algorithm)

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token,settings.secret_key,algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    payload = verify_access_token(token)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

    return db_user