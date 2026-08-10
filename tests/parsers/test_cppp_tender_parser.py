from pathlib import Path

from tender_intelligence_platform.parsers.cppp_tender_parser import (
    CPPPTenderParser,
)


FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "cppp_tender.html"
)

TENDER_URL = "https://eprocure.gov.in/eprocure/app"


def test_cppp_tender_parser():
    """Parser should produce a valid Tender from CPPP HTML."""

    html = FIXTURE_PATH.read_text(
        encoding="utf-8"
    )

    parser = CPPPTenderParser()

    tender = parser.parse(
        html,
        tender_url=TENDER_URL,
    )

    # Required identity fields
    assert tender.tender_id
    assert tender.tender_title
    assert tender.organization
    assert tender.tender_url

    # Dates should be extracted
    assert tender.published_date
    assert tender.bid_submission_start_date
    assert tender.bid_submission_end_date
    assert tender.opening_date

    # Monetary fields should be numeric
    assert isinstance(
        tender.estimated_value,
        (int, float),
    )

    assert isinstance(
        tender.earnest_money_deposit,
        (int, float),
    )

    assert isinstance(
        tender.tender_fee,
        (int, float),
    )

    # Classification fields
    assert tender.tender_type
    assert tender.category
    assert tender.procurement_type

    # Tender-specific fields
    assert tender.form_of_contract
    assert tender.payment_mode
    assert tender.work_location
    assert tender.work_description

    # Boolean field
    assert isinstance(
        tender.withdrawal_allowed,
        bool,
    )