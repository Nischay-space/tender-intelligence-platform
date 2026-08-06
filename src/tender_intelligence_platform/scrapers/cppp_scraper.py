from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.parsers.cppp_home_parser import (
    CPPPHomeParser,)
from tender_intelligence_platform.config.settings import settings
from tender_intelligence_platform.scrapers.base_scraper import BaseScraper


class CPPPScraper(BaseScraper):

    HOME_URL = "https://eprocure.gov.in/eprocure/app"

    def __init__(self, client: HTTPClient):
        super().__init__(client, settings)

        self._home_parser = CPPPHomeParser()

    def scrape(self) -> list[TenderLink]:

        self.log_progress("Downloading CPPP homepage")

        html = self.download(self.HOME_URL)

        tenders = self._home_parser.parse(html)

        self.log_progress(
            f"Found {len(tenders)} tenders."
        )

        return tenders