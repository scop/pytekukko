"""Pytekukko model objects."""

# Copyright 2021 Ville Skyttä

from datetime import date, timezone
from datetime import datetime as dt
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter
from pydantic.alias_generators import to_camel
from pydantic.functional_validators import BeforeValidator

SERVICE_TIMEZONE = ZoneInfo("Europe/Helsinki")
"""Time zone to use when converting UTC datetime timestamps to local dates."""

_DATETIME = TypeAdapter(dt)


def _to_local_date(value: str | dt) -> date:
    """Convert timestamp to date in the service time zone, ignoring the time of day."""
    parsed = value if isinstance(value, dt) else _DATETIME.validate_python(value)
    return (
        (parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed)
        .astimezone(SERVICE_TIMEZONE)
        .date()
    )


LocalDate = Annotated[date, BeforeValidator(_to_local_date)]
"""Date part of a timestamp that is expressed in the service time zone."""


class LoginResult(BaseModel):
    """LoginResult encapsulates a token and its expiration time."""

    model_config = ConfigDict(alias_generator=to_camel)

    token: str
    expires_at: dt


class Address(BaseModel):
    """Address encapsulates a postal address."""

    model_config = ConfigDict(alias_generator=to_camel)

    street: str
    post_office: str
    postal_code: str
    country_code: str


class Coordinates(BaseModel):
    """Coordinates encapsulates a map location."""

    model_config = ConfigDict(alias_generator=to_camel)

    x: float
    y: float


class ContactPerson(BaseModel):
    """ContactPerson encapsulates contact details for a container location."""

    model_config = ConfigDict(alias_generator=to_camel)

    name: str
    email: str | None = None
    phone_number: str | None = None
    bin_location_contact_person: str | None = None


class EInvoicing(BaseModel):
    """EInvoicing encapsulates electronic invoicing details."""

    model_config = ConfigDict(alias_generator=to_camel)

    address: str
    operator: str
    edi_code: str | None = None


class BuildingClassification(BaseModel):
    """BuildingClassification encapsulates a building classification code."""

    model_config = ConfigDict(alias_generator=to_camel)

    code: str
    name: str


class BuildingUsage(BaseModel):
    """BuildingUsage encapsulates a building usage code."""

    model_config = ConfigDict(alias_generator=to_camel)

    code: str


class EmptyingInfo(BaseModel):
    """EmptyingInfo encapsulates a customer's waste emptying details."""

    model_config = ConfigDict(alias_generator=to_camel)

    id: str
    name: str
    address: Address
    contract_date: LocalDate
    contract_end_date: LocalDate | None
    location_interrupt_date: LocalDate | None = None
    location_interrupt_end_date: LocalDate | None = None
    coordinates: Coordinates
    building_classification: BuildingClassification
    building_usage: BuildingUsage
    apartment_count: int
    resident_count: int
    composts: bool
    is_company: bool
    customer_price_list: str
    municipality_code: str
    invoicing_id: str
    contact_person: ContactPerson
    concern_id: str
    manager_id: str
    customer_group: str
    area: str
    # TODO(scop): shared_container: list, but of what, need sample
    contract_types: list[str] = []
    # TODO(scop): notifications: list, but of what, need sample


class BillingInfo(BaseModel):
    """BillingInfo encapsulates a customer's billing information."""

    model_config = ConfigDict(alias_generator=to_camel)

    id: str
    name: str
    address: Address
    contract_date: LocalDate
    contract_end_date: LocalDate | None
    coordinates: Coordinates | None = None
    is_company: bool
    company_id: str | None = None
    contact_person: ContactPerson | None = None
    e_invoicing: EInvoicing | None = None
    consumer_e_invoice_type: str | None = None
    invoice_type: str | None = None  # only seen in single billing-info responses
    billing_email: str | None = None
    billing_phone: str | None = None
    concern_id: str | None = None
    manager_id: str | None = None
    customer_group: str | None = None


class EmptyingInterval(BaseModel):
    """EmptyingInterval encapsulates a recurring emptying schedule period."""

    model_config = ConfigDict(alias_generator=to_camel)

    start_week: int
    end_week: int
    interval: int
    amount_per_week: int
    sequence: int


class Emptying(BaseModel):
    """Emptying encapsulates a single emptying event."""

    model_config = ConfigDict(alias_generator=to_camel)

    emptying_date: LocalDate
    event_type: str  # Planned, Successful, Missed
    description: str | None = None


class AllEmptyings(BaseModel):
    """AllEmptyings encapsulates emptying events by outcome."""

    model_config = ConfigDict(alias_generator=to_camel)

    # these come in PascalCase, unlike the rest of the API
    successful: list[Emptying] = Field(default_factory=list, alias="Successful")
    missed: list[Emptying] = Field(default_factory=list, alias="Missed")
    planned: list[Emptying] = Field(default_factory=list, alias="Planned")


class Price(BaseModel):
    """Price encapsulates the prices of a contract."""

    model_config = ConfigDict(alias_generator=to_camel)

    handling_price: Decimal
    handling_price_including_vat: Decimal
    handling_unit_price: Decimal
    handling_unit_price_including_vat: Decimal
    transport_price: Decimal
    transport_price_including_vat: Decimal
    transport_unit_price: Decimal
    transport_unit_price_including_vat: Decimal
    waste_tax_price: Decimal
    waste_tax_price_including_vat: Decimal
    waste_unit_tax_price: Decimal
    waste_unit_tax_price_including_vat: Decimal
    total_price_gross: Decimal
    total_price_net: Decimal


class Contract(BaseModel):
    """Contract encapsulates an emptying contract for a customer."""

    model_config = ConfigDict(alias_generator=to_camel)

    customer_id: str
    product_code: int
    position: int
    name: str
    service_name: str
    product_guid: str
    next_emptying: LocalDate | None = None
    emptying_intervals: list[EmptyingInterval]
    amount: Decimal
    unit: str  # Unknown, Piece
    size: str
    transport_price: Decimal
    handling_price: Decimal
    start_date: LocalDate
    end_date: LocalDate | None = None
    paused_from: LocalDate | None = None
    paused_to: LocalDate | None = None
    comment: str
    shared_container: bool
    readonly_contract: bool
    status: str  # Unspecified
    gate_key_code: str
    corresponding_person_id: str
    well_type: bool
    # only in single contract responses
    all_emptyings: AllEmptyings | None = None
    price: Price | None = None


class Invoice(BaseModel):
    """Invoice encapsulates information about a customer invoice."""

    model_config = ConfigDict(alias_generator=to_camel)

    invoice_number: int
    customer_number: str
    invoice_date: LocalDate
    due_date: LocalDate
    amount_open: Decimal
    amount_completed: Decimal
    currency: str
    billing_name: str
    payment_status: str
    payment_expired: bool
    payment_date: dt | None  # TODO(scop): LocalDate? non-null sample needed
