"""Jätekukko e-services client."""

# Copyright 2021 Ville Skyttä

from datetime import date
from datetime import datetime as dt
from http import HTTPStatus
from typing import Any, cast
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from aiohttp import ClientResponseError, ClientSession

from .exceptions import UnexpectedResponseStructureError
from .models import CollectionEvent, CustomerData, InvoiceHeader, Service, TokenInfo

__version__ = "0.17.1"
DEFAULT_BASE_URL = "https://asiointi.jatekukko.fi/api/customers/"
DEFAULT_TENANT_ID = "0431f4d4-5592-49c9-bcc8-51a6965b6851"
"""Jätekukko's tenant id in the service."""

SERVICE_TIMEZONE = ZoneInfo("Europe/Helsinki")
"""Assumed time zone of naive timestamps in data from service."""

_AUTH_SCHEME = "Vingo-e-services"


class Pytekukko:
    """Client for accessing Jätekukko e-services."""

    def __init__(
        self,
        session: ClientSession,
        username: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        token: TokenInfo | None = None,
    ):
        """Set up client.

        :param session: aiohttp client session to use
        :param username: e-services username
        :param password: e-services password
        :param base_url: base URL of the service API
        :param token: previously obtained token to use, see :attr:`token`
        """
        self.session: ClientSession = session
        self.username: str = username
        self.password: str = password
        self.base_url: str = base_url
        self.tenant_id: str = DEFAULT_TENANT_ID
        self.token: TokenInfo | None = token
        """Current authentication token.

        Set by :meth:`login`, cleared by :meth:`logout`. Can be persisted and passed
        to a new client to maintain the session across interpreter restarts.
        """

    async def get_customer_data(self) -> list[CustomerData]:
        """Get customer data."""
        url = urljoin(self.base_url, "Customers/emptying-infos")

        response_data = await self._request_with_retry(method="GET", url=url)
        if not isinstance(response_data, list | tuple):
            raise UnexpectedResponseStructureError(response_data)

        return [CustomerData(raw_data=_unmarshal(data)) for data in response_data]

    async def get_services(
        self,
        customer: CustomerData | str | None = None,
    ) -> list[Service]:
        """Get services.

        :param customer: the customer or a customer number to get services of;
            None to get services of all customers available to the user
        """
        if customer is None:
            customer_numbers = [
                a_customer.customer_number
                for a_customer in await self.get_customer_data()
            ]
        elif isinstance(customer, CustomerData):
            customer_numbers = [customer.customer_number]
        else:
            customer_numbers = [customer]

        services: list[Service] = []
        for customer_number in customer_numbers:
            url = urljoin(
                self.base_url,
                f"Customers/emptying-infos/{customer_number}/contracts",
            )
            response_data = await self._request_with_retry(method="GET", url=url)
            if not isinstance(response_data, list | tuple):
                raise UnexpectedResponseStructureError(response_data)
            services.extend(
                Service(raw_data=_unmarshal(service)) for service in response_data
            )

        return services

    async def get_collection_events(self, service: Service) -> list[CollectionEvent]:
        """Get past and planned collection events for a service.

        :param service: the service to get events for
        """
        url = urljoin(
            self.base_url,
            f"Customers/contracts/{service.customer_number}/{service.pos}",
        )

        response_data = await self._request_with_retry(method="GET", url=url)
        if not isinstance(response_data, dict):
            raise UnexpectedResponseStructureError(response_data)
        all_emptyings = cast(
            "dict[str, list[dict[str, Any]]]",
            response_data.get("allEmptyings", {}),
        )

        events = [
            CollectionEvent(raw_data=_unmarshal(event))
            for events_of_type in all_emptyings.values()
            for event in events_of_type
        ]
        events.sort(key=lambda event: event.date)
        return events

    async def get_collection_schedule(self, what: Service) -> list[date]:
        """Get collection schedule for a service.

        :param what: the service to get schedule for
        :returns: sorted dates of past and planned collections
        """
        return sorted({event.date for event in await self.get_collection_events(what)})

    async def get_invoice_headers(self) -> list[InvoiceHeader]:
        """Get headers of available invoices."""
        url = urljoin(self.base_url, "customers/invoices")

        response_data = await self._request_with_retry(method="GET", url=url)
        if not isinstance(response_data, list | tuple):
            raise UnexpectedResponseStructureError(response_data)

        return [
            InvoiceHeader(raw_data=_unmarshal(invoice_header))
            for invoice_header in response_data
        ]

    async def login(self) -> TokenInfo:
        """Log in, and store the obtained token in :attr:`token`."""
        url = urljoin(self.base_url, "Users/login")
        data = {"userName": self.username, "password": self.password}

        async with self.session.post(
            url,
            headers=self._headers(authenticated=False),
            json=data,
            raise_for_status=True,
        ) as response:
            response_data = await response.json()

        if not isinstance(response_data, dict) or "token" not in response_data:
            raise UnexpectedResponseStructureError(response_data)
        unmarshalled = _unmarshal(response_data)
        self.token = TokenInfo(
            token=cast("str", unmarshalled["token"]),
            expires_at=cast("dt", unmarshalled["expiresAt"]),
        )
        return self.token

    async def logout(self) -> None:
        """Log out the current session, and clear :attr:`token`."""
        if self.token is None:
            return
        url = urljoin(self.base_url, "Users/logout")

        try:
            async with self.session.post(
                url,
                headers=self._headers(),
                raise_for_status=True,
            ) as response:
                _ = await response.read()
        finally:
            self.token = None

    def _headers(self, *, authenticated: bool = True) -> dict[str, str]:
        """Get request headers."""
        headers = {
            "Accept": "application/json",
            "Accept-Language": "fi-FI, fi",
            "Tenant-Id": self.tenant_id,
        }
        if authenticated and self.token is not None:
            headers["Authorization"] = f"{_AUTH_SCHEME} {self.token.token}"
        return headers

    async def _request_with_retry(self, **request_kwargs: Any) -> Any:  # pyright: ignore[reportExplicitAny] # aiohttp kwargs type not public
        """Do a request, with automatic login and retry if not logged in.

        :param request_kwargs: kwargs to pass to self.session.request
        """
        if self.token is None or not self.token.is_valid():
            _ = await self.login()
        else:
            try:
                async with self.session.request(
                    **request_kwargs,
                    headers=self._headers(),
                    raise_for_status=True,
                ) as response:
                    return await response.json()
            except ClientResponseError as ex:
                if ex.status not in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                    raise
            _ = await self.login()

        async with self.session.request(
            **request_kwargs,
            headers=self._headers(),
            raise_for_status=True,
        ) as response:
            return await response.json()


# pyright: reportUnknownArgumentType=false, reportUnknownVariableType=false


def _unmarshal(data: Any) -> Any:  # pyright: ignore[reportExplicitAny] # by design
    """Unmarshal items in parsed JSON to more specific objects.

    ISO 8601 timestamps are converted to timezone aware datetimes in
    :data:`SERVICE_TIMEZONE`; naive ones are assumed to be in it already.

    :param data: parsed JSON data
    :return: copy of data, unmarshalled
    """
    if isinstance(data, str):
        try:
            parsed = dt.fromisoformat(data.replace("Z", "+00:00"))
        except ValueError:
            return data
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=SERVICE_TIMEZONE)
        return parsed.astimezone(SERVICE_TIMEZONE)
    if isinstance(data, dict):
        return {key: _unmarshal(value) for key, value in data.items()}
    if isinstance(data, list):
        return [_unmarshal(value) for value in data]
    return data
