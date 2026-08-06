from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.models.tender_link import TenderLink
from tender_intelligence_platform.parsers.cppp_home_parser import (
    CPPPHomeParser,)


class CPPPScraper:
    HOME_URL = "https://eprocure.gov.in/eprocure/app"

    def __init__(self, client: HTTPClient):
        self._client = client
        self._home_parser = CPPPHomeParser()

    def scrape_homepage(self) -> list[TenderLink]:
        response = self._client.get(self.HOME_URL)

        return self._home_parser.parse(response.text)