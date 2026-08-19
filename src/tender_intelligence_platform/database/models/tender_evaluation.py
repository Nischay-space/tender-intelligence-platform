from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from tender_intelligence_platform.database.base import Base
from tender_intelligence_platform.database.models.tender import TenderORM


class TenderEvaluationORM(Base):
    """SQLAlchemy representation of tender evaluation results."""

    __tablename__ = "tender_evaluations"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    tender_id: Mapped[int] = mapped_column(
        ForeignKey(
            "tenders.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    keyword_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    eligibility_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    final_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    matched_keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    excluded_keywords: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    passed_rules: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    failed_rules: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    unknown_rules: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    reasons: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    tender: Mapped["TenderORM"] = relationship(
        "TenderORM",
        back_populates="evaluation",
    )
    