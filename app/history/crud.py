from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ChatMessage

async def get_messages_by_session(session: AsyncSession, session_id: int):
    q = select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at)
    result = await session.execute(q)
    return result.scalars().all()

async def save_message(session: AsyncSession, session_id: int, role: str, text: str):
    msg = ChatMessage(session_id=session_id, role=role, text=text)
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg
