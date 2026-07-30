"""Pytekukko tests."""

# Copyright 2021 Ville Skyttä

import datetime
import os
from typing import Any, TypeVar

import pytest
from aiohttp import ClientSession

from pytekukko import Pytekukko
from pytekukko.examples import load_pytekukko_dotenv

T = TypeVar("T", bound=dict[str, Any])

FAKE_CUSTOMER_NUMBER = "00-0000000-00"
FAKE_PASSWORD = "secret"  # noqa: S105
FAKE_POS = "1234"

QUERY_PARAMETER_FILTERS = [
    ("customerId", FAKE_CUSTOMER_NUMBER),
    ("customerNumber", FAKE_CUSTOMER_NUMBER),
    ("pos", FAKE_POS),
]
POST_DATA_FILTERS = [
    ("j_username", FAKE_CUSTOMER_NUMBER),
    ("j_password", FAKE_PASSWORD),
]


def before_record_response(response: T) -> T:
    """Scrub unwanted data before recording response."""
    response["headers"].pop("Set-Cookie", None)

    if response["body"] != {} and any(
        "html" in h for h in response["headers"].get("Content-Type", [])
    ):
        response["body"]["string"] = b"redacted"  # unused, bloats cassettes

    return response


@pytest.fixture(scope="module", autouse=True)
def _load_dotenv() -> None:
    """Load our environment."""
    _ = load_pytekukko_dotenv()


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, Any]:
    """Get vcrpy configuration."""
    return {
        "before_record_response": before_record_response,
        "filter_headers": ["Cookie"],
        "filter_query_parameters": QUERY_PARAMETER_FILTERS,
        "filter_post_data_parameters": POST_DATA_FILTERS,
    }


@pytest.fixture(name="client")
async def fixture_client() -> Pytekukko:
    """Get a client."""
    return Pytekukko(
        session=ClientSession(),
        customer_number=os.environ.get(
            "PYTEKUKKO_CUSTOMER_NUMBER",
            FAKE_CUSTOMER_NUMBER,
        ),
        password=os.environ.get("PYTEKUKKO_PASSWORD", FAKE_PASSWORD),
    )


@pytest.mark.vcr
async def test_login_logout(client: Pytekukko) -> None:
    """Test login followed by logout."""
    async with client.session:
        assert await client.login()
        await client.logout()  # No exception counts as success here


@pytest.mark.vcr
async def test_logout(client: Pytekukko) -> None:
    """Test bare logout."""
    async with client.session:
        await client.logout()  # No exception counts as success here


@pytest.mark.vcr
async def test_get_collection_schedule(client: Pytekukko) -> None:
    """Test getting collection schedule."""
    async with client.session:
        dates = await client.get_collection_schedule(
            what=int(os.environ.get("PYTEKUKKO_TEST_POS", FAKE_POS)),
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
