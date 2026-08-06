from abc import ABC, abstractmethod
import logging

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.config.settings import Settings


class BaseScraper(ABC):
    """
    Base class for all website scrapers.

    Provides shared infrastructure while allowing each
    scraper to implement its own scraping workflow.
    """

    def __init__(
        self,
        client: HTTPClient,
        settings: Settings,
    ) -> None:
        self._client = client
        self._settings = settings
        self._logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def scrape(self):
        """
        Execute the scraping workflow.

        Must be implemented by every scraper.
        """
        raise NotImplementedError

    def download(self, url: str) -> str:
        """
        Download a webpage and return its HTML.
        """

        self._logger.info("Downloading %s", url)

        response = self._client.get(url)

        return response.text

    def log_progress(self, message: str) -> None:
        """
        Log scraper progress.
        """

        self._logger.info(message)

    def save_checkpoint(self) -> None:
        """
        Placeholder for future checkpoint implementation.
        """

        self._logger.debug("Checkpoint saved.")

    def load_checkpoint(self) -> None:
        """
        Placeholder for future checkpoint implementation.
        """

        self._logger.debug("Checkpoint loaded.")