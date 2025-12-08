from sqlmodel import create_engine, SQLModel, Session
from app.core.config import settings
import logging
from sqlalchemy.exc import SQLAlchemyError
import os
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

# Pooling configuration (tune via env vars)
DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "2"))
DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# Ensure TLS for Supabase and similar hosts. If the DATABASE_URL already
# contains sslmode, do not override it.
connect_args = {}
try:
    parsed = urlparse(settings.DATABASE_URL)
    if parsed.hostname and parsed.hostname.endswith("supabase.co"):
        # check for existing sslmode in query
        qs = parse_qs(parsed.query)
        if "sslmode" not in qs:
            connect_args["sslmode"] = "require"
except Exception:
    # If parsing fails, fall back to no special connect args
    pass

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_timeout=DB_POOL_TIMEOUT,
    pool_pre_ping=True,
    connect_args=connect_args,
)


def create_db_and_tables() -> None:
    try:
        SQLModel.metadata.create_all(engine)
    except SQLAlchemyError as exc:
        # Log the error but don't crash the app; this allows local dev to continue
        # when the remote DB is temporarily unreachable (e.g., DNS/network issues).
        logger.error("Could not create tables on database: %s", exc)


def get_session() -> Session:
    try:
        with Session(engine) as session:
            yield session
    except SQLAlchemyError:
        # If the DB is not available, raise an HTTP-friendly error at call time
        # (the dependency that uses this generator will surface an error).
        raise
