from fastapi import FastAPI
from .database import engine
from . import models
from .users import router as user_router

app = FastAPI()
app.include_router(user_router)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"hello world"}

