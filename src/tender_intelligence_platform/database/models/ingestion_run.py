from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tender_intelligence_platform.database.base import Base


class IngestionRunORM(Base):
    """SQLAlchemy representation of a single ingestion run's outcome."""

    __tablename__ = "ingestion_runs"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="RUNNING",
    )

    discovered: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    successful: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    failed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    skipped: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )