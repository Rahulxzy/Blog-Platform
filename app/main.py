from fastapi import FastAPI
from .database import engine
from . import models

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message":"hello world"}

