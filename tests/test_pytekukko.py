"""Pytekukko tests."""

# Copyright 2021 Ville Skyttä

import datetime
import json
import os
from typing import Any, TypeVar

import pytest
from aiohttp import ClientSession

from pytekukko import Pytekukko
from pytekukko.examples import load_pytekukko_dotenv
from pytekukko.models import Service

T = TypeVar("T", bound=dict[str, Any])

FAKE_USERNAME = "user@example.com"
FAKE_PASSWORD = "secret"  # noqa: S105
FAKE_CUSTOMER_NUMBER = "00-0000000-00"
FAKE_POS = 1


def before_record_request(request: Any) -> Any:  # pyright: ignore[reportExplicitAny] # vcr.request.Request not typed
    """Scrub unwanted data before recording request."""
    if request.body and request.uri.endswith("/Users/login"):
        request.body = json.dumps(
            {"userName": FAKE_USERNAME, "password": FAKE_PASSWORD},
        ).encode()
    return request


def before_record_response(response: T) -> T:
    """Scrub unwanted data before recording response."""
    response["headers"].pop("Set-Cookie", None)
    return response


@pytest.fixture(scope="module", autouse=True)
def _load_dotenv() -> None:
    """Load our environment."""
    _ = load_pytekukko_dotenv()


@pytest.fixture(scope="module")
def vcr_config() -> dict[str, Any]:
    """Get vcrpy configuration."""
    return {
        "before_record_request": before_record_request,
        "before_record_response": before_record_response,
        "filter_headers": ["Authorization", "Cookie"],
    }


@pytest.fixture(name="client")
async def fixture_client() -> Pytekukko:
    """Get a client."""
    return Pytekukko(
        session=ClientSession(),
        username=os.environ.get("PYTEKUKKO_USERNAME", FAKE_USERNAME),
        password=os.environ.get("PYTEKUKKO_PASSWORD", FAKE_PASSWORD),
    )


@pytest.mark.vcr
async def test_login_logout(client: Pytekukko) -> None:
    """Test login followed by logout."""
    async with client.session:
        token = await client.login()
        assert token.token
        assert token.is_valid()
        assert client.token is token
        await client.logout()  # No exception counts as success here
        assert client.token is None


@pytest.mark.vcr
async def test_logout(client: Pytekukko) -> None:
    """Test bare logout."""
    async with client.session:
        await client.logout()  # No exception counts as success here


@pytest.mark.vcr
async def test_get_customer_data(client: Pytekukko) -> None:
    """Test getting customer data."""
    async with client.session:
        customers = await client.get_customer_data()
    assert customers
    assert all(customer.customer_number for customer in customers)
    assert all(customer.name for customer in customers)


@pytest.mark.vcr
async def test_get_services(client: Pytekukko) -> None:
    """Test getting services."""
    async with client.session:
        services = await client.get_services()
    assert services
    assert all(service.name for service in services)
    assert all(isinstance(service.pos, int) for service in services)
    assert any(
        isinstance(service.next_collection, datetime.date) for service in services
    )


@pytest.mark.vcr
async def test_get_collection_schedule(client: Pytekukko) -> None:
    """Test getting collection schedule."""
    service = Service(
        raw_data={
            "customerId": os.environ.get(
                "PYTEKUKKO_TEST_CUSTOMER_NUMBER",
                FAKE_CUSTOMER_NUMBER,
            ),
            "position": int(os.environ.get("PYTEKUKKO_TEST_POS", FAKE_POS)),
        },
    )
    async with client.session:
        dates = await client.get_collection_schedule(what=service)
    assert dates
    assert all(isinstance(date, datetime.date) for date in dates)
    assert dates == sorted(dates)


@pytest.mark.vcr
async def test_get_invoice_headers(client: Pytekukko) -> None:
    """Test getting invoice headers."""
    async with client.session:
        invoice_headers = await client.get_invoice_headers()
    assert invoice_headers
    assert all(invoice_header.raw_data for invoice_header in invoice_headers)
    assert all(invoice_header.invoice_number for invoice_header in invoice_headers)
    assert all(invoice_header.name for invoice_header in invoice_headers)
    assert all(invoice_header.due_date for invoice_header in invoice_headers)
    assert all(
        isinstance(invoice_header.total, float) for invoice_header in invoice_headers
    )
