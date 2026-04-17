"""Data models for the Cyclus library."""

from dataclasses import dataclass, field
from datetime import date, datetime

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin

from cyclus.const import WasteType


@dataclass
class Address(DataClassORJSONMixin):
    """A resolved address returned by the address lookup endpoint."""

    bag_id: str = field(metadata=field_options(alias="bagid"))
    zipcode: str = field(metadata=field_options(alias="postcode"))
    house_number: int = field(metadata=field_options(alias="huisnummer"))
    house_letter: str = field(metadata=field_options(alias="huisletter"))
    house_number_addition: str = field(metadata=field_options(alias="toevoeging"))
    description: str
    street: str = field(metadata=field_options(alias="straat"))
    city: str = field(metadata=field_options(alias="woonplaats"))
    city_id: int = field(metadata=field_options(alias="woonplaatsId"))
    municipality_id: int = field(metadata=field_options(alias="gemeenteId"))
    latitude: float
    longitude: float


@dataclass
class WasteRegistration(DataClassORJSONMixin):
    """A single waste registration entry ("Mijn gegevens" tab)."""

    chip: str
    container: str
    timestamp: datetime = field(metadata=field_options(alias="tijdstip"))


@dataclass
class CalendarEvent(DataClassORJSONMixin):
    """A single pick-up event from the waste calendar."""

    waste_type: WasteType = field(metadata=field_options(alias="afvalstroom_id"))
    pickup_date: date = field(metadata=field_options(alias="ophaaldatum"))
