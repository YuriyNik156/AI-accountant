from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.database import get_async_session
from app import models
from app.schemas import UserCreate, UserLogin, Token
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_async_session)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await session.execute(
        models.User.__table__.select().where(models.User.id == int(user_id))
    )
    user = result.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Easy access
    return models.User(**user._mapping)


@router.post("/register", response_model=Token)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        models.User.__table__.select().where(models.User.username == user_data.username)
    )
    existing = result.fetchone()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed = hash_password(user_data.password)

    new_user = models.User(username=user_data.username, password_hash=hashed)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    token = create_access_token({"sub": str(new_user.id)})
    return Token(access_token=token)


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        models.User.__table__.select().where(models.User.username == user_data.username)
    )
    row = result.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = models.User(**row._mapping)

    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)
