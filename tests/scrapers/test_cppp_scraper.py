from pathlib import Path
from unittest.mock import MagicMock
from datetime import date

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.scrapers.cppp_scraper import CPPPScraper


FIXTURE_PATH = (
    Path(__file__).parent.parent
    / "parsers"
    / "fixtures"
    / "cppp_tender.html"
)


def test_scrape_detail():
    """Scraper should download and parse one tender."""

    html = FIXTURE_PATH.read_text(
        encoding="utf-8"
    )

    fake_response = MagicMock()

    fake_response.text = html

    fake_client = MagicMock(
        spec=HTTPClient
    )

    fake_client.get.return_value = (
        fake_response
    )

    scraper = CPPPScraper(
        fake_client,
        settings,
    )

    link = TenderLink(
        title="Test Tender",
        reference_number="TEST-001",
        detail_url=(
            "https://eprocure.gov.in/"
            "eprocure/app?test=1"
        ),
        closing_date=date(2026, 9, 3),
        opening_date=date(2026, 9, 7),
    )

    tender = scraper.scrape_detail(link)

    assert isinstance(
        tender,
        Tender,
    )

    assert tender.tender_id

    assert tender.tender_title

    assert tender.organization

    fake_client.get.assert_called_once_with(
        str(link.detail_url)
    )