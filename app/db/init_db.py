from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.session import engine


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def init_db() -> None:
    """Initialize database with seed data if needed."""
    create_tables()
