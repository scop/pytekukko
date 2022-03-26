"""Jätekukko Omakukko client."""

from datetime import date, datetime
from http import HTTPStatus
from typing import Any, Dict, List, Union, cast
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientResponseError, ClientSession

from .models import CustomerData, InvoiceHeader, Service

__version__ = "0.11.0"
DEFAULT_BASE_URL = "https://tilasto.jatekukko.fi/jatekukko/"


class Pytekukko:
    """Client for accessing Jätekukko Omakukko services."""

    def __init__(
        self,
        session: ClientSession,
        customer_number: str,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
    ):
        """Set up client."""
        self.session = session
        self.customer_number = customer_number
        self.password = password
        self.base_url = base_url

    async def get_customer_data(self) -> Dict[str, List[CustomerData]]:
        """Get customer data."""
        url = urljoin(self.base_url, "secure/get_customer_datas.do")

        response_data = await self._request_with_retry(method="GET", url=url)

        return {
            customer_number: [CustomerData(raw_data=a_data) for a_data in data]
            for customer_number, data in _unmarshal(response_data).items()
        }

    async def get_services(self) -> List[Service]:
        """Get services."""
        url = urljoin(self.base_url, "secure/get_services_by_customer_numbers.do")
        params = {"customerNumbers[]": self.customer_number}

        response_data = await self._request_with_retry(
            method="GET", url=url, params=params
        )
        assert isinstance(response_data, (list, tuple))

        return [Service(raw_data=_unmarshal(service)) for service in response_data]

    async def get_collection_schedule(self, what: Union[Service, int]) -> List[date]:
        """
        Get collection schedule for a service.

        :param what: the service or a "pos" value of one to get schedule for
        """
        url = urljoin(self.base_url, "get_collection_schedule.do")
        pos = what.pos if isinstance(what, Service) else what
        params = {"customerNumber": self.customer_number, "pos": pos}

        response_data = await self._request_with_retry(
            method="GET", url=url, params=params
        )

        return cast(List[date], _unmarshal(response_data))

    async def get_invoice_headers(self) -> List[InvoiceHeader]:
        """Get headers of available invoices."""
        url = urljoin(self.base_url, "secure/get_invoice_headers_for_customer.do")
        params = {
            "customerId": self.customer_number,  # yep, customerId, not *Number here
        }

        response_data = await self._request_with_retry(
            method="GET", url=url, params=params
        )
        assert isinstance(response_data, (list, tuple))

        return [
            InvoiceHeader(raw_data=_unmarshal(invoice_header))
            for invoice_header in response_data
        ]

    async def login(self) -> Dict[str, str]:
        """Log in."""
        url = urljoin(self.base_url, "j_acegi_security_check")
        headers = (("X-Requested-With", "XMLHttpRequest"),)
        params = {"target": "2"}
        data = {"j_username": self.customer_number, "j_password": self.password}

        async with self.session.post(
            url, headers=headers, params=params, data=data, raise_for_status=True
        ) as response:
            # TODO(scop): Check we got {"response":"OK"}?
            return cast(Dict[str, str], await response.json())

    async def logout(self) -> None:
        """Log out the current session."""
        url = urljoin(self.base_url, "j_acegi_logout_elcustrap")

        async with self.session.get(url, raise_for_status=True) as response:
            await _drain(response)

    async def _request_with_retry(self, **request_kwargs: Any) -> Any:
        """
        Do a request, with automatic login and retry if session is logged out.

        :param raise_for_first_status: whether first unsuccessful status should raise;
            False allows for handling special cases that give errors instead of
            redirecting to login page
        :param request_kwargs: kwargs to pass to self.session.request
        """
        try:
            async with self.session.request(
                **request_kwargs, raise_for_status=True
            ) as response:
                if response.history and response.url.path.endswith("/login.do"):
                    await _drain(response)
                else:
                    return await response.json()
        except ClientResponseError as ex:
            if not (
                ex.status in (HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR)
                and "get_collection_schedule" in ex.request_info.url.path
            ):
                raise

        _ = await self.login()
        async with self.session.request(
            **request_kwargs, raise_for_status=True
        ) as response:
            return await response.json()


def _unmarshal(data: Any) -> Any:
    """
    Unmarshal items in parsed JSON to more specific objects.

    :param data: parsed JSON data
    :return: unmarshalled data
    """
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = _unmarshal(value)
    elif isinstance(data, list):
        for i, value in enumerate(data):
            data[i] = _unmarshal(value)
    elif isinstance(data, str):
        try:
            data = datetime.strptime(data, "%Y-%m-%d").date()
        except ValueError:
            try:
                data = datetime.strptime(data, "%H:%M").time()
            except ValueError:
                pass
    return data


async def _drain(response: ClientResponse) -> None:
    """
    Consume and discard response.

    Useful for keeping the connection alive without caring about response content.
    """
    async for _ in response.content.iter_chunked(1024):
        pass
