"""
HTTP-related exceptions.

These exceptions hide the underlying HTTP library from the rest
of the application.
"""


class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""


class HTTPTimeoutError(HTTPClientError):
    """Raised when an HTTP request times out."""


class HTTPConnectionError(HTTPClientError):
    """Raised when a connection cannot be established."""


class HTTPResponseError(HTTPClientError):
    """Raised when a server returns an unsuccessful response."""