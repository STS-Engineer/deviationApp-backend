from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from urllib.parse import quote_plus
from app.core.config import settings

# URL-encode credentials to handle special characters
encoded_user = quote_plus(settings.DB_USER)
encoded_password = quote_plus(settings.DB_PASSWORD)

DATABASE_URL = (
    f"postgresql://{encoded_user}:"
    f"{encoded_password}@"
    f"{settings.DB_HOST}:"
    f"{settings.DB_PORT}/"
    f"{settings.DB_NAME}"
    f"?sslmode={settings.DB_SSLMODE}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
