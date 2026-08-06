"""
Reusable HTTP client.

This module centralizes all HTTP communication for the application.
Scrapers should never call the requests library directly.
"""

from __future__ import annotations

import logging

from requests import ConnectionError, HTTPError, Timeout
import requests

from tender_intelligence_platform.exceptions import (
    HTTPConnectionError,
    HTTPResponseError,
    HTTPTimeoutError,
)

from tender_intelligence_platform.config.settings import settings
from typing import Optional


logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Reusable HTTP client.

    Owns the HTTP session and provides a simple interface
    for making requests.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
    ) -> None:
        self._session = session or requests.Session()

        self._session.headers.update(
            {
                "User-Agent": settings.app_name,
                "Accept": "*/*",
            }
        )

    def get(self, url: str, **kwargs) -> requests.Response:
        """
        Send a GET request.

        Args:
            url: Target URL.

        Returns:
            HTTP response.
        """

        timeout = kwargs.pop("timeout", settings.http_timeout)

        logger.info("GET %s", url)

        try:
            response = self._session.get(
                url,
                timeout=timeout,
                **kwargs,
            )

            response.raise_for_status()

            return response

        except Timeout as exc:
            logger.exception("Request timed out: %s", url)
            raise HTTPTimeoutError(str(exc)) from exc

        except ConnectionError as exc:
            logger.exception("Connection failed: %s", url)
            raise HTTPConnectionError(str(exc)) from exc

        except HTTPError as exc:
            logger.exception("HTTP error: %s", url)
            raise HTTPResponseError(str(exc)) from exc

    def close(self) -> None:
        """Close the HTTP session."""
        self._session.close()