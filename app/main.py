from app.database import Base, engine
from app import models
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from AI-accountant!"}

models.Base.metadata.create_all(bind=engine)
