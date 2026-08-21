from collections.abc import Generator

from sqlalchemy.orm import Session

from tender_intelligence_platform.database.connection import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Provide a database session for a single API request.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()