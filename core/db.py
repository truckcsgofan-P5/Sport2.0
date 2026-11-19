from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.engine import make_url
from .config import setting

DATABASE_URL = setting("DATABASE_URL").strip()
if not DATABASE_URL:
    raise RuntimeError(
        "Chybí DATABASE_URL. Lokálně nastav .env, na Streamlit Cloud nastav Secrets."
    )

# Neon commonly supplies postgresql://; use the installed psycopg v3 driver.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

url = make_url(DATABASE_URL)
if url.drivername != "postgresql+psycopg":
    raise RuntimeError("SportStats 2.0 očekává PostgreSQL přes ovladač psycopg 3.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=3,
    max_overflow=2,
    future=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session():
    return SessionLocal()
