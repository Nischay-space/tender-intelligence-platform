from datetime import date
from uuid import uuid4

from tender_intelligence_platform.database.connection import SessionLocal
from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.repositories.tender_repository import (
    TenderRepository,
)


def make_tender() -> Tender:
    """Create a valid test Tender."""

    unique_id = f"TEST-{uuid4().hex[:8]}"

    return Tender(
        tender_id=unique_id,
        tender_title="Test Tender",
        organization="Test Organization",
        tender_reference_number="REF-001",
        tender_url="https://example.com/tender",
        published_date="10-Aug-2026 10:00 AM",
        bid_submission_start_date="10-Aug-2026 10:30 AM",
        bid_submission_end_date="20-Aug-2026 05:30 PM",
        opening_date="21-Aug-2026 11:00 AM",
        estimated_value=100000.0,
        earnest_money_deposit=2000.0,
        tender_fee=500.0,
        currency="INR",
        tender_type="Open Tender",
        category="Works",
        procurement_type="Works",
        state="Delhi",
        city="New Delhi",
        work_location="New Delhi",
        status="Open",
        withdrawal_allowed=True,
        form_of_contract="Item Rate",
        payment_mode="Offline",
        work_description="Test tender description",
    )


def test_create_and_get_tender():
    tender = make_tender()

    with SessionLocal() as session:
        repository = TenderRepository(session)

        created = repository.create(tender)

        session.commit()

        found = repository.get_by_tender_id(
            tender.tender_id
        )

        assert created.tender_id == tender.tender_id
        assert found is not None
        assert found.tender_title == "Test Tender"
        assert found.estimated_value == 100000.0


def test_update_tender():
    tender = make_tender()

    with SessionLocal() as session:
        repository = TenderRepository(session)

        repository.create(tender)
        session.commit()

        existing = repository.get_by_tender_id(
            tender.tender_id
        )

        assert existing is not None

        updated_tender = tender.model_copy(
            update={
                "tender_title": "Updated Tender",
                "estimated_value": 200000.0,
            }
        )

        repository.update(
            existing,
            updated_tender,
        )

        session.commit()

        updated = repository.get_by_tender_id(
            tender.tender_id
        )

        assert updated is not None
        assert updated.tender_title == "Updated Tender"
        assert updated.estimated_value == 200000.0


def test_upsert_creates_new_tender():
    tender = make_tender()

    with SessionLocal() as session:
        repository = TenderRepository(session)

        result = repository.upsert(tender)

        session.commit()

        assert result.tender_id == tender.tender_id

        found = repository.get_by_tender_id(
            tender.tender_id
        )

        assert found is not None


def test_upsert_updates_existing_tender():
    tender = make_tender()

    with SessionLocal() as session:
        repository = TenderRepository(session)

        repository.upsert(tender)
        session.commit()

        updated_tender = tender.model_copy(
            update={
                "tender_title": "Updated Through Upsert",
                "estimated_value": 500000.0,
            }
        )

        result = repository.upsert(
            updated_tender
        )

        session.commit()

        assert result.tender_title == (
            "Updated Through Upsert"
        )

        found = repository.get_by_tender_id(
            tender.tender_id
        )

        assert found is not None
        assert found.tender_title == (
            "Updated Through Upsert"
        )
        assert found.estimated_value == 500000.0