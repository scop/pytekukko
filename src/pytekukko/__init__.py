"""Jätekukko Omakukko client."""

# Copyright 2021 Ville Skyttä

from contextlib import suppress
from datetime import date
from datetime import datetime as dt
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from aiohttp import ClientResponse, ClientResponseError, ClientSession

from .exceptions import UnexpectedResponseStructureError
from .models import CustomerData, InvoiceHeader, LoginResult, Service

__version__ = "0.50.0"
DEFAULT_BASE_URL = "https://asiointi.jatekukko.fi/api/"
DEFAULT_TENANT_ID = "0431f4d4-5592-49c9-bcc8-51a6965b6851"

SERVICE_TIMEZONE = ZoneInfo("Europe/Helsinki")
"""Time zone to use when converting UTC datetime timestamps dates in local time."""


class Pytekukko:
    """Client for accessing Jätekukko Omakukko services."""

    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        tenant_id: str = DEFAULT_TENANT_ID,
    ):
        """Set up client."""
        self.session: ClientSession = session
        self.username: str = username
        self.password: str = password
        self.base_url: str = base_url
        self.tenant_id: str = tenant_id
        self._token: str | None = None
        self._token_expires_at: dt | None = None

    # TODO
    async def get_customer_data(self) -> dict[str, list[CustomerData]]:
        """Get customer data."""
        url = urljoin(self.base_url, "secure/get_customer_datas.do")

        response_data = await self._request_with_retry(method="GET", url=url)

        return {
            customer_number: [CustomerData(raw_data=a_data) for a_data in data]
            for customer_number, data in _unmarshal(response_data).items()
        }

    # TODO
    async def get_services(self) -> list[Service]:
        """Get services."""
        url = urljoin(self.base_url, "secure/get_services_by_customer_numbers.do")
        params = {"customerNumbers[]": self.customer_number}

        response_data = await self._request_with_retry(
            method="GET",
            url=url,
            params=params,
        )
        if not isinstance(response_data, list | tuple):
            raise UnexpectedResponseStructureError(response_data)

        return [Service(raw_data=_unmarshal(service)) for service in response_data]

    # TODO
    async def get_collection_schedule(self, what: Service | int) -> list[date]:
        """Get collection schedule for a service.

        :param what: the service or a "pos" value of one to get schedule for
        """
        url = urljoin(self.base_url, "get_collection_schedule.do")
        pos = what.pos if isinstance(what, Service) else what
        params = {"customerNumber": self.customer_number, "pos": pos}

        response_data = await self._request_with_retry(
            method="GET",
            url=url,
            params=params,
        )

        return cast("list[date]", _unmarshal(response_data))

    # TODO
    async def get_invoice_headers(self) -> list[InvoiceHeader]:
        """Get headers of available invoices."""
        url = urljoin(self.base_url, "secure/get_invoice_headers_for_customer.do")
        params = {
            "customerId": self.customer_number,  # yep, customerId, not *Number here
        }

        response_data = await self._request_with_retry(
            method="GET",
            url=url,
            params=params,
        )
        if not isinstance(response_data, list | tuple):
            raise UnexpectedResponseStructureError(response_data)

        return [
            InvoiceHeader(raw_data=_unmarshal(invoice_header))
            for invoice_header in response_data
        ]

    async def login(self) -> LoginResult:
        """Log in."""
        url = urljoin(self.base_url, "customers/Users/login")
        headers = (("Tenant-Id", self.tenant_id),)
        data = {"userName": self.username, "password": self.password}

        async with self.session.post(
            url,
            headers=headers,
            json=data,
            raise_for_status=True,
        ) as response:
            rj = await response.json()
            return LoginResult(
                token=rj["token"],
                expires_at=dt.fromisoformat(rj["expiresAt"]),
            )

    async def logout(self) -> None:
        """Log out the current session."""
        url = urljoin(self.base_url, "customers/Users/logout")

        async with self.session.post(url, raise_for_status=True) as response:
            await _drain(response)

    async def _request_with_retry(self, **request_kwargs: Any) -> Any:  # pyright: ignore[reportExplicitAny] # aiohttp kwargs type not public
        """Do a request, with automatic login and retry if session is logged out.

        :param request_kwargs: kwargs to pass to self.session.request
        """
        async def _do_request() -> Any:
            async with self.session.request(
                **request_kwargs,
                raise_for_status=True,
            ) as response:
                return await response.json()
        try:
            return await _do_request()
        except ClientResponseError as ex:
            if ex.status != HTTPStatus.UNAUTHORIZED:
                raise

        _ = await self.login()
        return await _do_request()


# pyright: reportUnknownArgumentType=false, reportUnknownVariableType=false


def _unmarshal(data: Any) -> Any:  # pyright: ignore[reportExplicitAny] # by design
    """Unmarshal items in parsed JSON to more specific objects.

    :param data: parsed JSON data
    :return: copy of data, unmarshalled
    """
    if isinstance(data, str):
        try:
            parsed = dt.strptime(data, "%Y-%m-%d").replace(tzinfo=SERVICE_TIMEZONE)
            return parsed.date()
        except ValueError:
            with suppress(ValueError):
                parsed = dt.strptime(data, "%H:%M").replace(tzinfo=SERVICE_TIMEZONE)
                return parsed.time()
    if isinstance(data, dict):
        return {key: _unmarshal(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_unmarshal(value) for value in data]
    return data


async def _drain(response: ClientResponse) -> None:
    """Consume and discard response.

    Useful for keeping the connection alive without caring about response content.
    """
    async for _ in response.content.iter_chunked(1024):
        pass
