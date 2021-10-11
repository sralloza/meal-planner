"""Database basic connections."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..core.config import settings

if "sqlite" in settings.DATABASE_URI:  # noqa
    connect_args = {"check_same_thread": False}
else:  # noqa
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URI, pool_pre_ping=True, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
