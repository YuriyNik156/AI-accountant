from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionBase(BaseModel):
    title: str


class SessionCreate(BaseModel):
    title: str = "Без названия"


class SessionOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatQueryRequest(BaseModel):
    message: str
    session_id: int

class ChatQueryResponse(BaseModel):
    answer: str
