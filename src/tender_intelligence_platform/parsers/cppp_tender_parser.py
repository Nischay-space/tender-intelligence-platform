import re

from bs4 import BeautifulSoup, Tag

from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.parsers.base_parser import BaseParser
from tender_intelligence_platform.parsers.table_parser import TableParser


class CPPPTenderParser(BaseParser):
    """Parse a CPPP tender detail page into a Tender model."""

    HTML_PARSER = "html.parser"

    SECTION_NAMES = (
        "Basic Details",
        "Critical Dates",
        "Tender Fee Details",
        "EMD Fee Details",
        "Work Item Details",
    )

    def parse(
        self,
        raw_data: str,
        tender_url: str,
    ) -> Tender:
        """Parse one CPPP tender detail page."""

        soup = BeautifulSoup(
            raw_data,
            self.HTML_PARSER,
        )

        details = self._extract_sections(soup)

        return self._build_tender(
            details=details,
            tender_url=tender_url,
        )

    def _extract_sections(
        self,
        soup: BeautifulSoup,
    ) -> dict[str, str]:
        """Extract all relevant CPPP fields."""

        details: dict[str, str] = {}

        # The tender details live inside this form.
        container = soup.select_one(
            "#DisplayTenderDetails"
        )

        if container is None:
            container = soup

        tables = container.select(
            "table.tablebg"
        )

        for table in tables:
            details.update(
                TableParser.parse(table)
            )

        return details

    def _build_tender(
        self,
        details: dict[str, str],
        tender_url: str,
    ) -> Tender:
        """Convert raw CPPP fields into our Tender model."""

        tender_id = self._required(
            details,
            "Tender ID",
        )

        title = self._required(
            details,
            "Title",
        )

        organization = details.get(
            "Organisation Chain"
        )

        tender_reference = details.get(
            "Tender Reference Number"
        )

        published_date = details.get(
            "Published Date"
        )

        submission_start = details.get(
            "Bid Submission Start Date"
        )

        submission_end = details.get(
            "Bid Submission End Date"
        )

        opening_date = details.get(
            "Bid Opening Date"
        )

        tender_value = self._parse_amount(
            details.get("Tender Value in ₹")
        )

        emd_amount = self._parse_amount(
            details.get("EMD Amount in ₹")
        )

        tender_fee = self._parse_amount(
            details.get("Tender Fee in ₹")
        )

        category = details.get(
            "Tender Category"
        )

        procurement_type = self._get_procurement_type(
            category
        )

        work_location = details.get(
            "Location"
        )

        return Tender(
            tender_id=tender_id,
            tender_title=title,
            organization=organization,
            tender_reference_number=tender_reference,
            tender_url=tender_url,

            published_date=published_date,
            bid_submission_start_date=submission_start,
            bid_submission_end_date=submission_end,
            opening_date=opening_date,

            estimated_value=tender_value,
            earnest_money_deposit=emd_amount,
            tender_fee=tender_fee,
            currency="INR",

            tender_type=details.get(
                "Tender Type"
            ),
            category=category,
            procurement_type=procurement_type,

            work_location=work_location,

            status="Open",

            withdrawal_allowed=self._parse_bool(
                details.get("Withdrawal Allowed")
            ),

            form_of_contract=details.get(
                "Form Of Contract"
            ),

            payment_mode=details.get(
                "Payment Mode"
            ),

            work_description=details.get(
                "Work Description"
            ),
        )

    @staticmethod
    def _required(
        details: dict[str, str],
        field: str,
    ) -> str:
        """Return a required field or raise a useful error."""

        value = details.get(field)

        if not value:
            raise ValueError(
                f"Required CPPP field missing: {field}"
            )

        return value

    @staticmethod
    def _parse_amount(
        value: str | None,
    ) -> float | None:
        """Convert Indian formatted monetary values to float."""

        if not value:
            return None

        cleaned = re.sub(
            r"[^\d.]",
            "",
            value,
        )

        if not cleaned:
            return None

        return float(cleaned)

    @staticmethod
    def _parse_bool(
        value: str | None,
    ) -> bool | None:
        """Convert CPPP Yes/No values to booleans."""

        if value is None:
            return None

        normalized = value.strip().lower()

        if normalized == "yes":
            return True

        if normalized == "no":
            return False

        return None

    @staticmethod
    def _get_procurement_type(
        category: str | None,
    ) -> str | None:
        """Normalize CPPP tender category."""

        if not category:
            return None

        normalized = category.strip().lower()

        if "work" in normalized:
            return "Works"

        if "service" in normalized:
            return "Services"

        if "goods" in normalized:
            return "Goods"

        return category