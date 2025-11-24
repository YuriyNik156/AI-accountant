from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import SessionCreate, SessionOut
from app.auth.router import get_current_user

router = APIRouter(prefix="/history", tags=["History"])


# 1. GET /history/sessions
@router.get("/sessions", response_model=list[SessionOut])
def get_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sessions = (
        db.query(models.SessionHistory)
        .filter(models.SessionHistory.user_id == current_user.id)
        .order_by(models.SessionHistory.created_at.desc())
        .all()
    )
    return sessions


# 2. GET /history/sessions/{id}
@router.get("/sessions/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.id == session_id,
            models.SessionHistory.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    return session


# 3. DELETE /history/sessions/{id}
@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.id == session_id,
            models.SessionHistory.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    db.delete(session)
    db.commit()

    return {"status": "deleted"}


# 4. PUT /history/sessions/{id}/title
@router.put("/sessions/{session_id}/title", response_model=SessionOut)
def update_title(
    session_id: int,
    data: SessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = (
        db.query(models.SessionHistory)
        .filter(
            models.SessionHistory.id == session_id,
            models.SessionHistory.user_id == current_user.id
        )
        .first()
    )

    if not session:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    session.title = data.title
    db.commit()
    db.refresh(session)

    return session
