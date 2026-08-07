from pydoc import html

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.parsers.cppp_home_parser import CPPPHomeParser
from tender_intelligence_platform.parsers.cppp_tender_parser import CPPPTenderParser
from tender_intelligence_platform.scrapers.base_scraper import BaseScraper


class CPPPScraper(BaseScraper[TenderLink, Tender]):

    def __init__(
        self,
        client: HTTPClient,
    ):

        super().__init__(client, settings)

        self._home_parser = CPPPHomeParser()
        self._tender_parser = CPPPTenderParser()

    def scrape_homepage(
        self,
    ) -> list[TenderLink]:

        html = self.download(
            self._settings.cppp_home_url
        )

        return self._home_parser.parse(html)

    def scrape_detail(
        self,
        link: TenderLink,
    ) -> dict[str, str]:

        html = self.download(str(link.detail_url))

        details = self._tender_parser.parse(html)

        print("\n" + "=" * 80)
        print(f"TENDER : {link.reference_number}")
        print("=" * 80)

        for key, value in details.items():
            print(f"{key:<35} : {value}")

        print("=" * 80 + "\n")

        return details