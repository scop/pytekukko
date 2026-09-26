"""Pytekukko tests."""

# Copyright 2021 Ville Skyttä

import json
import os
import re
from typing import Any, TypeVar
import uuid

import pytest
from aiohttp import ClientSession
from vcr.request import Request

from pytekukko import _AUTH_HEADER, Pytekukko
from pytekukko.examples import load_pytekukko_dotenv

T = TypeVar("T", bound=dict[str, Any])

TEST_USERNAME = "test-username"
TEST_PASSWORD = "test-password"  # noqa: S105
TEST_TOKEN = "test-token"  # noqa: S105
TEST_CUSTOMER_ID = "00-0000000-00"
TEST_POSITION = 42

invoice_number = 0


def _gen_invoice_number() -> int:
    global invoice_number
    invoice_number += 1
    return invoice_number


amount_open = 10.0


def _gen_amount_open() -> float:
    global amount_open
    amount_open += 0.01
    return amount_open


product_guid = 0


def _gen_product_guid() -> str:
    global product_guid
    product_guid += 1
    return str(uuid.UUID(int=product_guid))


HEADER_FILTERS = [
    ("Authorization", _AUTH_HEADER.format(TEST_TOKEN)),
    ("Cookie", None),
]
POST_DATA_FILTERS = [
    ("userName", TEST_USERNAME),
    ("password", TEST_PASSWORD),
]
RESPONSE_DATA_FILTERS = [
    ("amountOpen", _gen_amount_open),
    ("billingName", "Test Name"),
    ("comment", "Hello world!"),
    ("customerId", TEST_CUSTOMER_ID),
    ("customerNumber", TEST_CUSTOMER_ID),
    ("invoiceNumber", _gen_invoice_number),
    ("position", TEST_POSITION),
    ("productGuid", _gen_product_guid),
    ("token", TEST_TOKEN),
]


def before_record_request(request: Request) -> Request:
    """Scrub unwanted data before recording request."""
    for prop, replacement in (
        ("PYTEKUKKO_TEST_CUSTOMER_ID", TEST_CUSTOMER_ID),
        ("PYTEKUKKO_TEST_POSITION", str(TEST_POSITION)),
    ):
        if value := os.environ.get(prop):
            request.uri = re.sub(
                "/" + re.escape(value) + r"\b", f"/{replacement}", request.uri
            )
    return request


def before_record_response(response: T) -> T:
    """Scrub unwanted data before recording response."""
    response["headers"].pop("Set-Cookie", None)

    if response["body"].get("string"):
        try:
            data = json.loads(response["body"]["string"])
        except ValueError:
            return response
        if isinstance(data, list):
            data = data[-3:]
        for prop, redaction in RESPONSE_DATA_FILTERS:
            if isinstance(data, dict):
                if prop in data:
                    value = redaction() if callable(redaction) else redaction
                    data[prop] = value
            else:
                for item in data:
                    if prop in item:
                        value = redaction() if callable(redaction) else redaction
                        item[prop] = value
        response["body"]["string"] = json.dumps(data).encode()

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
        "filter_headers": HEADER_FILTERS,
        "filter_post_data_parameters": POST_DATA_FILTERS,
    }


@pytest.fixture(name="client")
async def fixture_client() -> Pytekukko:
    """Get a client."""
    return Pytekukko(
        session=ClientSession(),
        username=os.environ.get(
            "PYTEKUKKO_USERNAME",
            TEST_USERNAME,
        ),
        password=os.environ.get("PYTEKUKKO_PASSWORD", TEST_PASSWORD),
    )


@pytest.mark.vcr
async def test_login_logout(client: Pytekukko) -> None:
    """Test login followed by logout."""
    async with client.session:
        _ = await client.login()
        await client.logout()


@pytest.mark.vcr
async def test_logout(client: Pytekukko) -> None:
    """Test bare logout."""
    async with client.session:
        await client.logout()  # No exception counts as success here


@pytest.mark.vcr
async def test_contract(client: Pytekukko) -> None:
    """Test getting contract."""
    async with client.session:
        _ = await client.contract(
            os.environ.get("PYTEKUKKO_TEST_CUSTOMER_ID", TEST_CUSTOMER_ID),
            int(os.environ.get("PYTEKUKKO_TEST_POSITION", TEST_POSITION)),
        )


@pytest.mark.vcr
async def test_contracts(client: Pytekukko) -> None:
    """Test getting contracts."""
    async with client.session:
        _ = await client.contracts(
            os.environ.get("PYTEKUKKO_TEST_CUSTOMER_ID", TEST_CUSTOMER_ID)
        )


@pytest.mark.vcr
async def test_invoices(client: Pytekukko) -> None:
    """Test getting invoices."""
    async with client.session:
        _ = await client.invoices()
