from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from urllib.parse import quote_plus
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

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

logger.info(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

# Use connection pooling optimized for Azure
engine = create_engine(
    DATABASE_URL,
    pool_size=5,  # Reduced for Azure
    max_overflow=10,  # Max overflow connections
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,  # Recycle connections every hour
    echo=False,  # Set to True for SQL logging (disable in production)
    connect_args={
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()
