from unittest.mock import MagicMock
import pytest
import requests

from tender_intelligence_platform.clients.http_client import HTTPClient
from tender_intelligence_platform.exceptions import HTTPTimeoutError
from tender_intelligence_platform.exceptions import HTTPConnectionError


def test_get_success():
    fake_session = MagicMock(spec=requests.Session)
    fake_session.headers = {}

    fake_response = MagicMock(spec=requests.Response)
    fake_response.raise_for_status.return_value = None

    fake_session.get.return_value = fake_response

    client = HTTPClient(session=fake_session)

    response = client.get("https://example.com")

    assert response is fake_response

    fake_session.get.assert_called_once()

    import pytest





def test_timeout_exception():
    fake_session = MagicMock(spec=requests.Session)
    fake_session.headers = {}

    fake_session.get.side_effect = requests.Timeout()

    client = HTTPClient(session=fake_session)

    with pytest.raises(HTTPTimeoutError):
        client.get("https://example.com")

def test_connection_exception():
    fake_session = MagicMock(spec=requests.Session)
    fake_session.headers = {}

    fake_session.get.side_effect = requests.ConnectionError()

    client = HTTPClient(session=fake_session)

    with pytest.raises(HTTPConnectionError):
        client.get("https://example.com")

def test_close_session():
    fake_session = MagicMock(spec=requests.Session)
    fake_session.headers = {}

    client = HTTPClient(session=fake_session)

    client.close()

    fake_session.close.assert_called_once()