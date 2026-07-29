"""
Application exception hierarchy.
"""

from .http import (
    HTTPClientError,
    HTTPConnectionError,
    HTTPResponseError,
    HTTPTimeoutError,
)

__all__ = [
    "HTTPClientError",
    "HTTPConnectionError",
    "HTTPResponseError",
    "HTTPTimeoutError",
]