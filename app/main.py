from fastapi import FastAPI
from .database import engine
from . import models
from .auth import router as auth_router
from .posts import router as post_router
from .comments import router as comment_router


app = FastAPI()
models.Base.metadata.create_all(bind=engine)
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/")
def home():
    return {"message":"hello world"}

