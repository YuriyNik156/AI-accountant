from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer

from app.database import Base, engine
from app import models

from app.auth.router import router as auth_router
from app.history.routes import router as history_router

print(">>> MAIN.PY LOADED <<<")

# --- Создаём приложение ---
app = FastAPI(
    title="AI Accountant API",
    version="1.0.0",
    description="Backend with JWT authentication and history CRUD"
)

# --- Создаём таблицы ---
models.Base.metadata.create_all(bind=engine)

# --- Подключаем роутеры ---
app.include_router(auth_router)
app.include_router(history_router)

# --- Простой тестовый эндпоинт ---
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

    # Добавляем BearerAuth ко всем эндпоинтам автоматически
    for path_data in openapi_schema.get("paths", {}).values():
        for operation in path_data.values():
            # Только если security ещё нет — не перезаписываем вручную заданное
            operation.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
