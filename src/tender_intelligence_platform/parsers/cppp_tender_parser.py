from bs4 import BeautifulSoup

from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.parsers.base_parser import BaseParser


class CPPPParser(BaseParser):

    HTML_PARSER = "html.parser"

    def parse(self, raw_data: str) -> Tender:
        soup = BeautifulSoup(raw_data, self.HTML_PARSER)

        return Tender(
            tender_id=self._extract_tender_id(soup),
            title=self._extract_title(soup),
            organization=self._extract_organization(soup),
            tender_url=self._extract_tender_url(soup),

            # Temporary placeholders
            procurement_type=...,
            tender_type=...,
            status=...,
        )

    def _extract_tender_id(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

    def _extract_title(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

    def _extract_organization(self, soup: BeautifulSoup) -> str:
        raise NotImplementedError

    def _extract_tender_url(self, soup: BeautifulSoup):
        raise NotImplementedError