from fastapi import FastAPI
from .auth import router as auth_router
from .posts import router as post_router
from .comments import router as comment_router


app = FastAPI(title="Blog Platform API",
              description="REST API for a blog platform with authentication, posts, and comments.",
              version="1.0.0")
app.include_router(auth_router)
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/")
def home():
    return {"message":"hello world"}

