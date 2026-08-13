from tender_intelligence_platform.models.tender import Tender
from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.parsers.cppp_home_parser import (
    CPPPHomeParser,
)
from tender_intelligence_platform.parsers.cppp_tender_parser import (
    CPPPTenderParser,
)
from tender_intelligence_platform.scrapers.base_scraper import BaseScraper


class CPPPScraper(BaseScraper):
    """Scraper for the Central Public Procurement Portal."""

    BASE_URL = "https://eprocure.gov.in"

    HOME_URL = (
        "https://eprocure.gov.in/eprocure/app"
    )

    def __init__(
        self,
        client,
        settings,
    ):
        super().__init__(client, settings)

        self._home_parser = CPPPHomeParser()
        self._tender_parser = CPPPTenderParser()

    def scrape_homepage(self) -> list[TenderLink]:
        """Scrape active tender links."""

        html = self.download(self.HOME_URL)

        return self._home_parser.parse(html)

    def scrape_detail(
        self,
        link: TenderLink,
    ) -> Tender:
        """Scrape and parse one tender detail page."""

        html = self.download(
            str(link.detail_url)
        )

        return self._tender_parser.parse(
            html,
            tender_url=str(link.detail_url),
        )   