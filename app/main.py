from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

import asyncio

from app.database import engine
from app import models

from app.auth.router import router as auth_router
from app.history.routes import router as history_router
from app.chat.router import router as chat_router
from fastapi.middleware.cors import CORSMiddleware


print(">>> MAIN.PY LOADED <<<")


# ======================================================
#         АСИНХРОННАЯ ИНИЦИАЛИЗАЦИЯ БАЗЫ
# ======================================================

async def init_models():
    """
    Создаёт все таблицы через AsyncEngine.
    Вызывается один раз при старте приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


# ======================================================
#                 СОЗДАНИЕ ПРИЛОЖЕНИЯ
# ======================================================

app = FastAPI(
    title="AI Accountant API",
    version="1.0.0",
    description="Backend with JWT authentication and history CRUD"
)

# ------------------------------------------------------
#                     CORS FIX
# ------------------------------------------------------

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # Только явные адреса
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Инициализация БД перед стартом сервера
@app.on_event("startup")
async def on_startup():
    await init_models()


# ======================================================
#                 ПОДКЛЮЧЕНИЕ РОУТЕРОВ
# ======================================================

app.include_router(auth_router)
app.include_router(history_router)
app.include_router(chat_router)


# ======================================================
#                    ТЕСТОВЫЙ ЭНДПОИНТ
# ======================================================

@app.get("/")
def root():
    return {"message": "AI-accountant backend is running!"}


# ======================================================
#                SWAGGER JWT AUTH FIX
# ======================================================

bearer_scheme = HTTPBearer()


def custom_openapi():
    """
    Добавляет BearerAuth в Swagger UI
    и автоматически подвязывает ко всем защищённым эндпоинтам.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Добавляем описание схемы авторизации
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Автоматически добавляем BearerAuth ко всем операциям
    for path_data in openapi_schema.get("paths", {}).values():
        for operation in path_data.values():
            operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
