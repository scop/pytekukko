"""Pytekukko model objects."""

# Copyright 2021 Ville Skyttä

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, cast


def _as_date(value: datetime | date | None) -> date | None:
    """Convert an unmarshalled timestamp to a date, if present."""
    if isinstance(value, datetime):
        return value.date()
    return value


@dataclass
class TokenInfo:
    """TokenInfo encapsulates an authentication token.

    Tokens are obtained by logging in, and can be persisted and set on a client to
    avoid logging in again on every run.
    """

    token: str
    expires_at: datetime

    def is_valid(self, *, margin_seconds: float = 120) -> bool:
        """Check whether the token is valid, with a margin before expiry."""
        now = datetime.now(tz=self.expires_at.tzinfo)
        return (self.expires_at - now).total_seconds() > margin_seconds


@dataclass
class CustomerData:
    """CustomerData encapsulates customer information.

    In the service, this is known as an "emptying info": a customer relationship
    tied to a collection location.

    Some frequently used attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: dict[str, Any]  # pyright: ignore[reportExplicitAny] # various

    @property
    def customer_number(self) -> str:
        """Get customer number."""
        return cast("str", self.raw_data["id"])

    @property
    def name(self) -> str:
        """Get customer name."""
        return cast("str", self.raw_data["name"])

    @property
    def street_address(self) -> str | None:
        """Get street address of the collection location."""
        address = cast("dict[str, Any] | None", self.raw_data.get("address"))
        return cast("str | None", address.get("street")) if address else None


@dataclass
class Service:
    """Service encapsulates information about parts of a customer relationship.

    In the service, these are known as "contracts". Examples of the kinds of services
    there are include collections of different kinds of waste containers, and yearly
    base prices for houses.

    Some frequently used service attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: dict[str, Any]  # pyright: ignore[reportExplicitAny] # various

    @property
    def customer_number(self) -> str:
        """Get customer number the service belongs to."""
        return cast("str", self.raw_data["customerId"])

    @property
    def name(self) -> str:
        """Get service name."""
        return cast("str", self.raw_data["name"])

    @property
    def pos(self) -> int:
        """Get "pos" value, the position of the service within the customer."""
        return cast("int", self.raw_data["position"])

    @property
    def next_collection(self) -> date | None:
        """Get next collection date.

        :returns: Next collection date, None if not applicable for the service.
        """
        return _as_date(self.raw_data.get("nextEmptying"))


@dataclass
class CollectionEvent:
    """CollectionEvent encapsulates a past or planned collection of a service."""

    raw_data: dict[str, Any]  # pyright: ignore[reportExplicitAny] # various

    @property
    def date(self) -> date:
        """Get collection date."""
        return cast("date", _as_date(self.raw_data["emptyingDate"]))

    @property
    def event_type(self) -> str:
        """Get event type, one of "Planned", "Successful", or "Missed"."""
        return cast("str", self.raw_data["eventType"])

    @property
    def description(self) -> str | None:
        """Get event description, if any."""
        return cast("str | None", self.raw_data.get("description"))


@dataclass
class InvoiceHeader:
    """InvoiceHeader encapsulates basic information of an invoice.

    Some frequently used attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: dict[str, Any]  # pyright: ignore[reportExplicitAny] # various

    @property
    def invoice_number(self) -> int:
        """Get invoice number."""
        return cast("int", self.raw_data["invoiceNumber"])

    @property
    def customer_number(self) -> str:
        """Get customer number."""
        return cast("str", self.raw_data["customerNumber"])

    @property
    def name(self) -> str:
        """Get billing name."""
        return cast("str", self.raw_data["billingName"])

    @property
    def invoice_date(self) -> date:
        """Get invoice date."""
        return cast("date", _as_date(self.raw_data["invoiceDate"]))

    @property
    def due_date(self) -> date:
        """Get due date."""
        return cast("date", _as_date(self.raw_data["dueDate"]))

    @property
    def total(self) -> float:
        """Get total amount, open and completed."""
        return cast("float", self.raw_data["amountOpen"]) + cast(
            "float", self.raw_data.get("amountCompleted") or 0
        )
