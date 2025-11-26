import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.database import get_async_session
from app.history.crud import get_messages_by_session, save_message

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


AI_URL = "http://127.0.0.1:8001/assistant/query"  # реальный AI, пока не используется


@router.post("/query", response_model=ChatQueryResponse)
async def query_ai(
    payload: ChatQueryRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    ВРЕМЕННАЯ ЗАГЛУШКА
    Позволяет фронту работать без внешнего сервиса AI.
    """

    # 1. Читаем историю из БД
    history_records = await get_messages_by_session(session, payload.session_id)

    history = [
        {"role": m.role, "text": m.text}
        for m in history_records
    ]

    # Добавляем текущее сообщение в историю
    history.append({"role": "user", "text": payload.message})

    # 2. Генерируем временный ответ (mock)
    answer_text = f"Заглушка: ты написал — '{payload.message}'. Всё работает! 🚀"

    # 3. Сохраняем user + assistant сообщения в БД
    await save_message(session, payload.session_id, "user", payload.message)
    await save_message(session, payload.session_id, "assistant", answer_text)

    # 4. Возвращаем ответ фронту
    return ChatQueryResponse(answer=answer_text)

@router.get("/history/{session_id}")
async def get_history(session_id: int, session: AsyncSession = Depends(get_async_session)):
    records = await get_messages_by_session(session, session_id)
    return [
        {"role": m.role, "text": m.text, "created_at": m.created_at.isoformat()}
        for m in records
    ]
