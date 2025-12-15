import os

AI_BASE_URL = os.getenv("AI_BASE_URL")
AI_API_KEY = os.getenv("AI_API_KEY")
AI_TIMEOUT = float(os.getenv("AI_TIMEOUT", 35.0))

if not AI_BASE_URL or not AI_API_KEY:
    raise RuntimeError("AI_BASE_URL или AI_API_KEY не заданы в окружении")
