# mock_ai.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Mock AI Service", version="1.0")

# Схема запроса от твоего эндпоинта
class AIRequest(BaseModel):
    question: str
    history: List[Dict[str, str]]  # [{"role": "user"/"assistant", "text": ...}]

# Схема ответа
class AIResponse(BaseModel):
    answer: str

@app.post("/assistant/query", response_model=AIResponse)
async def mock_query(data: AIRequest):
    # Просто возвращаем эхо-ответ + количество сообщений в истории
    history_len = len(data.history)
    return AIResponse(answer=f"[Mock AI] Вы спросили: {data.question}. История сообщений: {history_len} шт.")
