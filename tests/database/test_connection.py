from sqlalchemy import text

from tender_intelligence_platform.database.connection import engine


def test_database_connection():
    """Application should be able to connect to PostgreSQL."""

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT 1")
        )

        assert result.scalar() == 1