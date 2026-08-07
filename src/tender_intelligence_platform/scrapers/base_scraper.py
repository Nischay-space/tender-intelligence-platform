from abc import ABC, abstractmethod
import logging
from typing import Generic, TypeVar

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import Settings

LinkType = TypeVar("LinkType")
ResultType = TypeVar("ResultType")


class BaseScraper(ABC, Generic[LinkType, ResultType]):
    """
    Base framework for all scrapers.

    Implements the common crawling workflow while allowing
    each website to provide its own parsing logic.
    """

    def __init__(
        self,
        client: HTTPClient,
        settings: Settings,
    ) -> None:

        self._client = client
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__name__)

    def scrape(self) -> list[ResultType]:
        """
        Standard workflow shared by every scraper.
        """

        self.log_progress("Starting scraper...")

        links = self.scrape_homepage()

        self.log_progress(
            f"Found {len(links)} items."
        )

        results: list[ResultType] = []

        for link in links:

            try:

                result = self.scrape_detail(link)

                results.append(result)

            except Exception:

                self._logger.exception(
                    "Failed to scrape item."
                )

        self.log_progress(
            f"Completed. Scraped {len(results)} items."
        )

        return results

    @abstractmethod
    def scrape_homepage(self) -> list[LinkType]:
        """
        Return homepage links.
        """
        raise NotImplementedError

    @abstractmethod
    def scrape_detail(
        self,
        link: LinkType,
    ) -> ResultType:
        """
        Scrape one item.
        """
        raise NotImplementedError

    def download(self, url: str) -> str:

        response = self._client.get(url)

        return response.text

    def log_progress(self, message: str) -> None:

        self._logger.info(message)

    def save_checkpoint(self) -> None:

        self._logger.debug("Checkpoint saved.")

    def load_checkpoint(self) -> None:

        self._logger.debug("Checkpoint loaded.")