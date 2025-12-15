from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app import models
from app.schemas import SessionCreate, SessionOut
from app.auth.router import get_current_user
from app.history.crud import get_messages_by_session

router = APIRouter(prefix="/history", tags=["History"])


# 1. GET /history/sessions
@router.get("/sessions", response_model=list[SessionOut])
async def get_sessions(
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    query = (
        select(models.Session)
        .where(models.Session.user_id == current_user.id)
        .order_by(models.Session.created_at.desc())
    )

    result = await session.execute(query)
    sessions = result.scalars().all()

    return sessions


# 2. GET /history/sessions/{session_id}
@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    query = (
        select(models.Session)
        .where(
            models.Session.id == session_id,
            models.Session.user_id == current_user.id
        )
    )
    result = await session.execute(query)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    return session_obj


# 3. DELETE /history/sessions/{session_id}
@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    query = (
        select(models.Session)
        .where(
            models.Session.id == session_id,
            models.Session.user_id == current_user.id
        )
    )
    result = await session.execute(query)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    await session.delete(session_obj)
    await session.commit()

    return {"status": "deleted"}


# 4. PUT /history/sessions/{session_id}/title
@router.put("/sessions/{session_id}/title", response_model=SessionOut)
async def update_title(
    session_id: int,
    data: SessionCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    query = (
        select(models.Session)
        .where(
            models.Session.id == session_id,
            models.Session.user_id == current_user.id
        )
    )
    result = await session.execute(query)
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    session_obj.title = data.title
    await session.commit()
    await session.refresh(session_obj)

    return session_obj


# 5. POST /history/sessions/create  (только для тестов)
@router.post("/sessions/create", response_model=SessionOut)
async def create_session(
    data: SessionCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    new_session = models.Session(
        user_id=current_user.id,
        title=data.title
    )

    session.add(new_session)
    await session.commit()
    await session.refresh(new_session)

    return new_session


@router.get("/sessions/{session_id}/messages")
async def get_messages(
    session_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: models.User = Depends(get_current_user)
):
    # проверяем, что сессия принадлежит пользователю
    result = await session.execute(
        select(models.Session).where(
            models.Session.id == session_id,
            models.Session.user_id == current_user.id
        )
    )
    session_obj = result.scalar_one_or_none()

    if not session_obj:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    return session_obj.messages
