from fastapi import FastAPI
from app.database import Base, engine
from app import models
from app.auth.router import router as auth_router
from app.history.router import router as history_router

print(">>> MAIN.PY LOADED <<<")

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

app.include_router(history_router)

@app.get("/")
def root():
    return {"message": "AI-accountant backend is running!"}
