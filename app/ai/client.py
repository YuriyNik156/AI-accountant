import httpx
from app.core.config import AI_BASE_URL, AI_API_KEY, AI_TIMEOUT


async def ask_ai_assistant(
    query: str,
    session_id: str,
    history: list
) -> dict:
    async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
        response = await client.post(
            f"{AI_BASE_URL}/assistant/query",
            headers={
                "Content-Type": "application/json",
                "X-API-Key": AI_API_KEY
            },
            json={
                "query": query,
                "session_id": session_id,
                "history": history
            }
        )
        response.raise_for_status()
        return response.json()
