from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite для MVP
DATABASE_URL = "sqlite:///./app.db"

# Для PostgreSQL — просто заменить строку:
# DATABASE_URL = "postgresql+psycopg2://user:password@localhost/dbname"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# Dependency — используется в роутерах
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
