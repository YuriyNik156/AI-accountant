import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.database import get_async_session
from app.history.crud import get_messages_by_session, save_message

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


AI_URL = "http://127.0.0.1:8001/assistant/query"  # адрес сервиса промпт-инженера


@router.post("/query", response_model=ChatQueryResponse)
async def query_ai(
    payload: ChatQueryRequest,
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Достаём историю
    history_records = await get_messages_by_session(session, payload.session_id)

    history = [
        {"role": m.role, "text": m.text}
        for m in history_records
    ]

    # Добавляем новое сообщение пользователя в историю перед отправкой
    history.append({"role": "user", "text": payload.message})

    # 2. Отправляем запрос к API промпт-инженера
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                AI_URL,
                json={
                    "question": payload.message,
                    "history": history
                }
            )
    except Exception as e:
        raise HTTPException(500, f"Ошибка при обращении к AI-сервису: {e}")

    if response.status_code != 200:
        raise HTTPException(500, f"AI вернул ошибку {response.status_code}: {response.text}")

    data = response.json()
    answer_text = data.get("answer")

    if not answer_text:
        raise HTTPException(500, "AI вернул пустой ответ")

    # 3. Сохраняем user + assistant сообщения в базу
    await save_message(session, payload.session_id, "user", payload.message)
    await save_message(session, payload.session_id, "assistant", answer_text)

    # 4. Возвращаем ответ фронту
    return ChatQueryResponse(answer=answer_text)
