from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatQueryRequest, ChatQueryResponse
from app.database import get_async_session
from app.history.crud import get_messages_by_session, save_message
from app.ai.client import ask_ai_assistant
from app.auth.utils import get_current_user_id

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])


@router.post("/query", response_model=ChatQueryResponse)
async def query_ai(
    payload: ChatQueryRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_async_session),
    ):
    # 1. Загружаем историю
    await get_messages_by_session(
        session,
        session_id=payload.session_id,
        user_id=user_id
    )

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
