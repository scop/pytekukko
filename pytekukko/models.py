"""Pytekukko model objects."""

from dataclasses import dataclass
from datetime import date
from typing import Any, Dict, Optional, cast


@dataclass
class Service:
    """
    Service encapsulates information about parts of a customer relationship.

    Examples of the kinds of services there are include collections of different kinds
    of waste containers, and yearly base prices for houses.

    Some frequently used service attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: Dict[str, Any]

    @property
    def name(self) -> str:
        """Get service name."""
        return cast(str, self.raw_data["ASTNimi"])

    @property
    def pos(self) -> int:
        """Get "pos" value."""
        return cast(int, self.raw_data["ASTPos"])

    @property
    def next_collection(self) -> Optional[date]:
        """
        Get next collection date.

        :returns: Next collection date, None if not applicable for the service.
        """
        return self.raw_data.get("ASTSeurTyhj")


@dataclass
class CustomerData:
    """
    CustomerData encapsulates customer information.

    Some frequently used service attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: Dict[str, Any]

    @property
    def customer_number(self) -> str:
        """Get customer number."""
        return cast(str, self.raw_data["asiakasnro"])


@dataclass
class InvoiceHeader:
    """
    InvoiceHeader encapsulates basic information of an invoice.

    Some frequently used service attributes are available as individual properties,
    and all data retrieved from the service is available in the ``raw_data`` dict.
    """

    raw_data: Dict[str, Any]
