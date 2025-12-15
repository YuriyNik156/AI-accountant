from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.database import get_async_session
from app.history.crud import get_messages_by_session, save_message
from app.ai.client import ask_ai_assistant

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/query", response_model=ChatQueryResponse)
async def query_ai(
    payload: ChatQueryRequest,
    session: AsyncSession = Depends(get_async_session)
):
    # 1. Загружаем историю
    history_records = await get_messages_by_session(session, payload.session_id)

    history = [
        {
            "role": m.role,
            "content": m.text
        }
        for m in history_records[-5:]  # максимум 5 сообщений
    ]

    # 2. Вызываем AI
    try:
        ai_response = await ask_ai_assistant(
            query=payload.message,
            session_id=str(payload.session_id),
            history=history
        )
    except Exception as e:
        # fallback
        ai_response = {
            "answer": "AI-ассистент временно недоступен. Попробуйте позже.",
            "tokens_used": 0,
            "category": "error"
        }

    answer_text = ai_response["answer"]

    # 3. Сохраняем сообщения
    await save_message(session, payload.session_id, "user", payload.message)
    await save_message(session, payload.session_id, "assistant", answer_text)

    # 4. Возвращаем фронту
    return ChatQueryResponse(answer=answer_text)
