"""Pytekukko tests."""

import datetime
import os
from typing import Any, Dict, TypeVar
from urllib.parse import parse_qs, quote_plus, urlparse, urlunparse

import pytest
from aiohttp import ClientSession

from pytekukko import Pytekukko
from pytekukko.examples import load_pytekukko_dotenv

T = TypeVar("T", bound=Dict[str, Any])  # pylint: disable=invalid-name

FAKE_CUSTOMER_NUMBER = "00-0000000-00"
FAKE_PASSWORD = "secret"  # noqa: S105
FAKE_POS = "1234"

QUERY_PARAMETER_FILTERS = [
    ("customerId", FAKE_CUSTOMER_NUMBER),
    ("customerNumber", FAKE_CUSTOMER_NUMBER),
    ("pos", FAKE_POS),
]


def before_record_response(response: T) -> T:
    """Scrub unwanted data before recording response."""

    response["headers"].pop("Set-Cookie", None)

    # As of vcrpy 4.1.1, query parameters filtered with filter_query_parameters
    # do not end up filtered in response["url"], so address them here.
    url_parts = urlparse(response["url"])
    new_query_parts = []
    query_params = parse_qs(url_parts.query)
    for key, values in query_params.items():
        for filter_key, filter_value in QUERY_PARAMETER_FILTERS:
            if key == filter_key:
                values = [filter_value]
        for value in values:
            new_query_parts.append(f"{quote_plus(key)}={quote_plus(value)}")
    new_url_parts = list(url_parts)
    new_url_parts[4] = "&".join(new_query_parts)
    response["url"] = urlunparse(new_url_parts)

    if response["url"].endswith("/login.do"):
        response["body"]["string"] = b"redacted"  # unused, bloats cassettes

    return response


@pytest.fixture(scope="module", autouse=True)
def load_dotenv() -> None:
    """Load our environment."""
    _ = load_pytekukko_dotenv()


@pytest.fixture(scope="module")
def vcr_config() -> Dict[str, Any]:
    """Get vcrpy configuration."""
    return {
        "before_record_response": before_record_response,
        "filter_headers": ["Cookie"],
        "filter_query_parameters": QUERY_PARAMETER_FILTERS,
        # NOTE: this should be uncommented when upgrading vcrpy to a fixed > 4.1.1:
        #   https://github.com/kevin1024/vcrpy/issues/398
        #   https://github.com/kevin1024/vcrpy/pull/582
        #   https://github.com/kevin1024/vcrpy/pull/581
        # "filter_post_data_parameters": ["j_username", "j_password"],
    }


@pytest.fixture(name="client", scope="function")
async def fixture_client() -> Pytekukko:
    """Get a client."""
    return Pytekukko(
        session=ClientSession(),
        customer_number=os.environ.get(
            "PYTEKUKKO_CUSTOMER_NUMBER", FAKE_CUSTOMER_NUMBER
        ),
        password=os.environ.get("PYTEKUKKO_PASSWORD", FAKE_PASSWORD),
    )


@pytest.mark.vcr
async def test_login(client: Pytekukko) -> None:
    """Test login."""
    async with client.session:
        result = await client.login()
    assert result


@pytest.mark.vcr
async def test_logout(client: Pytekukko) -> None:
    """Test logout."""
    # TODO(scop): would be better to test from a logged in session
    async with client.session:
        await client.logout()
    # No exception counts as success here


@pytest.mark.vcr
async def test_get_collection_schedule(client: Pytekukko) -> None:
    """Test getting collection schedule."""
    async with client.session:
        dates = await client.get_collection_schedule(
            what=int(os.environ.get("PYTEKUKKO_TEST_POS", FAKE_POS))
        )
    assert dates
    assert all(isinstance(date, datetime.date) for date in dates)


@pytest.mark.vcr
async def test_get_invoice_headers(client: Pytekukko) -> None:
    """Test getting invoice headers."""
    async with client.session:
        invoice_headers = await client.get_invoice_headers()
    assert invoice_headers
    assert all(invoice_header.raw_data for invoice_header in invoice_headers)
    assert all(invoice_header.name for invoice_header in invoice_headers)
    assert all(invoice_header.due_date for invoice_header in invoice_headers)
    assert all(invoice_header.total for invoice_header in invoice_headers)
