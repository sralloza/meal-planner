"""Database dependencies."""

from contextlib import contextmanager

from ..db.session import SessionLocal, engine


def get_db():
    """Creates a local database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()


manual_db = contextmanager(get_db)
