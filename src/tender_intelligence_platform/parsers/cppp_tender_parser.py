from bs4 import BeautifulSoup

from tender_intelligence_platform.parsers.base_parser import BaseParser
from tender_intelligence_platform.parsers.table_parser import TableParser


class CPPPTenderParser(BaseParser):
    """
    Parses the CPPP tender detail page.

    Stage 1:
        HTML -> Dictionary

    Stage 2:
        Dictionary -> Tender
    """

    HTML_PARSER = "html.parser"

    def parse(self, raw_data: str) -> dict[str, str]:
        """
        Parse the tender detail page and return
        all extracted fields as a dictionary.
        """

        soup = BeautifulSoup(raw_data, self.HTML_PARSER)

        basic_details = self._extract_section(
            soup,
            "Basic Details",
        )

        critical_dates = self._extract_section(
            soup,
            "Critical Dates",
        )

        fee_details = self._extract_section(
            soup,
            "Tender Fee Details",
        )

        emd_details = self._extract_section(
            soup,
            "EMD Details",
        )

        work_item_details = self._extract_section(
            soup,
            "Work Item Details",
        )

        all_details = {
            **basic_details,
            **critical_dates,
            **fee_details,
            **emd_details,
            **work_item_details,
        }

        return all_details

    def _extract_section(
        self,
        soup: BeautifulSoup,
        section_name: str,
    ) -> dict[str, str]:
        """
        Extract one table section by heading.

        Example:
            Basic Details
            Critical Dates
            EMD Details
        """

        heading = soup.find(
            string=lambda text: text and section_name in text
        )

        if heading is None:
            return {}

        table = heading.find_next("table")

        if table is None:
            return {}

        return TableParser.parse(table)