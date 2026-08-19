from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tender_intelligence_platform.database.base import Base

class TenderEvaluation(Base):
    """Stores the filtering and eligibility evaluation of a tender."""

    __tablename__ = "tender_evaluations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    tender_id: Mapped[int] = mapped_column(
        ForeignKey("tenders.id"),
        nullable=False,
        unique=True,
    )

    keyword_relevant: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    matched_keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    excluded_keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    eligibility_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    final_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    reasons: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    tender = relationship(
        "Tender",
        back_populates="evaluation",
    )