from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# --- Настройки БД ---
DATABASE_URL = "sqlite+aiosqlite:///./app.db"

# --- Создаём async engine ---
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    echo=False
)

# --- Создаём async sessionmaker ---
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()


# --- Dependency для FastAPI ---
async def get_async_session():
    async with AsyncSessionLocal() as session:
        yield session
