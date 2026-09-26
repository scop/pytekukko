"""Jätekukko Omakukko client."""

# Copyright 2021 Ville Skyttä

from datetime import datetime as dt
from http import HTTPStatus
from typing import Any
from urllib.parse import quote, urljoin

from aiohttp import ClientResponse, ClientResponseError, ClientSession
from pydantic import TypeAdapter

from .models import (
    BillingInfo,
    Contract,
    EmptyingInfo,
    Invoice,
    LoginResult,
)

__version__ = "0.50.0"
DEFAULT_BASE_URL = "https://asiointi.jatekukko.fi/api/"
DEFAULT_TENANT_ID = "0431f4d4-5592-49c9-bcc8-51a6965b6851"

_AUTH_HEADER = "Vingo-e-services {}"

_BILLING_INFOS = TypeAdapter(list[BillingInfo])
_CONTRACTS = TypeAdapter(list[Contract])
_EMPTYING_INFOS = TypeAdapter(list[EmptyingInfo])
_INVOICES = TypeAdapter(list[Invoice])


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
            rt = await response.text()
            res = LoginResult.model_validate_json(rt)
            self.session.headers["Authorization"] = _AUTH_HEADER.format(res.token)
            return res

    async def refresh_login(self) -> LoginResult:
        """Refresh the login token."""
        url = urljoin(self.base_url, "customers/Users/refresh-login")

        async with self.session.post(
            url,
            raise_for_status=True,
        ) as response:
            rt = await response.text()
            res = LoginResult.model_validate_json(rt)
            self.session.headers["Authorization"] = _AUTH_HEADER.format(res.token)
            return res

    async def logout(self) -> None:
        """Log out the current session."""
        url = urljoin(self.base_url, "customers/Users/logout")

        async with self.session.post(url, raise_for_status=True) as response:
            await _drain(response)
            self.session.headers.pop("Authorization", None)

    async def billing_infos(self) -> list[BillingInfo]:
        """Get billing information."""
        url = urljoin(self.base_url, "customers/Customers/billing-infos")
        response_text = await self._request_with_retry(method="GET", url=url)
        return _BILLING_INFOS.validate_json(response_text)

    async def contract(self, customer_id: str, position: int) -> Contract:
        """Get a single contract.

        :param customer_id: the customer id, e.g. emptying info id
        :param position: the contract position, see Contract.position
        """
        url = urljoin(
            self.base_url,
            f"customers/Customers/contracts/{quote(customer_id, safe='')}/{position}",
        )
        response_text = await self._request_with_retry(method="GET", url=url)
        return Contract.model_validate_json(response_text)

    async def contracts(self, customer_id: str) -> list[Contract]:
        """Get contracts.

        :param customer_id: the customer id, e.g. emptying info id
        """
        url = urljoin(
            self.base_url,
            "customers/Customers/emptying-infos/"
            + quote(customer_id, safe="")
            + "/contracts",
        )
        response_text = await self._request_with_retry(method="GET", url=url)
        return _CONTRACTS.validate_json(response_text)

    async def emptying_infos(self) -> list[EmptyingInfo]:
        """Get emptying information."""
        url = urljoin(self.base_url, "customers/Customers/emptying-infos")
        response_text = await self._request_with_retry(method="GET", url=url)
        return _EMPTYING_INFOS.validate_json(response_text)

    async def invoices(self) -> list[Invoice]:
        """Get invoices."""
        url = urljoin(self.base_url, "customers/Customers/invoices")
        response_text = await self._request_with_retry(method="GET", url=url)
        return _INVOICES.validate_json(response_text)

    async def _request_with_retry(self, **request_kwargs: Any) -> str:  # pyright: ignore[reportExplicitAny] # aiohttp kwargs type not public
        """Do a request, with automatic login and retry if session is logged out.

        :param request_kwargs: kwargs to pass to self.session.request
        """

        async def _do_request() -> str:
            async with self.session.request(
                **request_kwargs,
                raise_for_status=True,
            ) as response:
                return await response.text()

        try:
            return await _do_request()
        except ClientResponseError as ex:
            if ex.status != HTTPStatus.UNAUTHORIZED:
                raise

        _ = await self.login()
        return await _do_request()


async def _drain(response: ClientResponse) -> None:
    """Consume and discard response.

    Useful for keeping the connection alive without caring about response content.
    """
    async for _ in response.content.iter_chunked(1024):
        pass
