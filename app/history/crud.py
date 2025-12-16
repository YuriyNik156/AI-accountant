from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Session, Message


# Создать новую сессию
async def create_session(db: AsyncSession, user_id: int, title: str | None = None) -> Session:
    new_session = Session(user_id=user_id, title=title)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session


# Получить все сессии пользователя
async def get_sessions(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Session).where(Session.user_id == user_id).order_by(Session.created_at.desc())
    )
    return result.scalars().all()


# Получить одну сессию
async def get_session(db: AsyncSession, session_id: int) -> Session | None:
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    return result.scalars().first()


# Переименовать сессию
async def rename_session(db: AsyncSession, session_id: int, new_title: str):
    session = await get_session(db, session_id)
    if session:
        session.title = new_title
        await db.commit()
        return session
    return None


# Удалить сессию
async def delete_session(db: AsyncSession, session_id: int):
    session = await get_session(db, session_id)
    if session:
        await db.delete(session)
        await db.commit()
        return True
    return False


# ============ МЕССЕДЖИ ============

async def save_message(db: AsyncSession, session_id: int, role: str, text: str):
    msg = Message(session_id=session_id, role=role, text=text)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def get_messages_by_session(
    db: AsyncSession,
    session_id: int,
    user_id: int
):
    result = await db.execute(
        select(Message)
        .join(Session, Session.id == Message.session_id)
        .where(
            Message.session_id == session_id,
            Session.user_id == user_id
        )
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()

