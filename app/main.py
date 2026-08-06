from fastapi import FastAPI
from .database import engine
from . import models
from . auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"hello world"}

