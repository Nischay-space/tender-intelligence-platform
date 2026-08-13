from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from tender_intelligence_platform.database.base import Base


class TenderORM(Base):
    """SQLAlchemy representation of a tender."""

    __tablename__ = "tenders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    tender_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    tender_title: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    organization: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    tender_reference_number: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    tender_url: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    published_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bid_submission_start_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    bid_submission_end_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    opening_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    estimated_value: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    earnest_money_deposit: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    tender_fee: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    tender_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    procurement_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    work_location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    withdrawal_allowed: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    form_of_contract: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    payment_mode: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    work_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    nullable=False,
)

updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=lambda: datetime.now(timezone.utc),
    onupdate=lambda: datetime.now(timezone.utc),
    nullable=False,
)