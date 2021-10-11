from sqlalchemy_utils import create_database, database_exists

from .base_class import Base
from .session import engine


def create_db_and_tables():
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.create_all(bind=engine)
