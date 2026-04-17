"""Tests for CyclusClient."""

from __future__ import annotations

from typing import TYPE_CHECKING

import aiohttp
from aioresponses import aioresponses
import pytest

from cyclus import CyclusClient
from cyclus.const import WasteType
from cyclus.exceptions import CyclusError
from tests import load_fixture, load_fixture_json
from tests.const import BAG_ID, HOUSE_NUMBER, LOGIN_CODE, ZIPCODE

if TYPE_CHECKING:
    from syrupy import SnapshotAssertion

BASE = "https://cyclusnv.nl"
ADDRESS_URL = f"{BASE}/adressen/{ZIPCODE}:{HOUSE_NUMBER}"
WASTE_REG_URL = f"{BASE}/diftar/afvalregistraties"
CALENDAR_URL = f"{BASE}/rest/adressen/{BAG_ID}/kalender/2025"


def test_waste_type_canonical_ids() -> None:
    """Test that canonical WasteType IDs resolve to the correct enum member."""
    assert WasteType(1) is WasteType.GFT
    assert WasteType(14) is WasteType.PMD


def test_waste_type_gouda_child_mapped() -> None:
    """Test that Gouda-specific child IDs map to their canonical parent."""
    assert WasteType(129) is WasteType.GFT
    assert WasteType(491) is WasteType.RESIDUAL_WASTE
    assert WasteType(385) is WasteType.PAPER
    assert WasteType(439) is WasteType.PMD
    assert WasteType(727) is WasteType.CHRISTMAS_TREES


def test_waste_type_unknown_raises() -> None:
    """Test that an unknown WasteType ID raises a ValueError."""
    with pytest.raises(ValueError, match="9999"):
        WasteType(9999)


async def test_get_bag_id(client: CyclusClient, responses: aioresponses) -> None:
    """Test resolving a BAG ID from a zipcode and house number."""
    responses.get(ADDRESS_URL, payload=load_fixture_json("address.json"))

    assert await client.get_bag_id(ZIPCODE, HOUSE_NUMBER) == BAG_ID


async def test_get_bag_id_sets_bag_id_on_client(
    client: CyclusClient, responses: aioresponses
) -> None:
    """Test that get_bag_id stores the resolved BAG ID on the client."""
    responses.get(ADDRESS_URL, payload=load_fixture_json("address.json"))

    await client.get_bag_id(ZIPCODE, HOUSE_NUMBER)

    assert client.bag_id == BAG_ID


async def test_get_bag_id_raises_when_not_found(
    client: CyclusClient, responses: aioresponses
) -> None:
    """Test that get_bag_id raises when no address is found."""
    responses.get(ADDRESS_URL, payload=[])

    with pytest.raises(CyclusError):
        await client.get_bag_id(ZIPCODE, HOUSE_NUMBER)


async def test_get_waste_registrations_raises_without_bag_id(
    client: CyclusClient,
) -> None:
    """Test that get_waste_registrations raises when no bag_id is set."""
    with pytest.raises(CyclusError):
        await client.get_waste_registrations(LOGIN_CODE)


async def test_get_waste_registrations_empty(
    client: CyclusClient, responses: aioresponses
) -> None:
    """Test that an empty registration response returns an empty list."""
    client.bag_id = BAG_ID
    responses.get(BASE, status=200)
    responses.post(
        WASTE_REG_URL,
        body=load_fixture("waste_registrations_empty.json").encode(),
    )

    result = await client.get_waste_registrations(LOGIN_CODE)

    assert result == []


async def test_get_waste_registrations(
    client: CyclusClient,
    responses: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving waste registrations."""
    client.bag_id = BAG_ID
    responses.get(BASE, status=200)
    responses.post(
        WASTE_REG_URL,
        body=load_fixture("waste_registrations.json").encode(),
    )

    result = await client.get_waste_registrations(LOGIN_CODE)

    assert result == snapshot


async def test_get_calendar_events_raises_without_bag_id(
    client: CyclusClient,
) -> None:
    """Test that get_calendar_events raises when no bag_id is set."""
    with pytest.raises(CyclusError):
        await client.get_calendar_events(2025)


async def test_get_calendar_events(
    client: CyclusClient,
    responses: aioresponses,
    snapshot: SnapshotAssertion,
) -> None:
    """Test retrieving calendar events."""
    client.bag_id = BAG_ID
    responses.get(CALENDAR_URL, body=load_fixture("kalender.json").encode())

    result = await client.get_calendar_events(2025)

    assert result == snapshot


async def test_get_calendar_events_waste_type_resolved(
    client: CyclusClient, responses: aioresponses
) -> None:
    """Test that calendar event waste type IDs resolve to WasteType enum members."""
    client.bag_id = BAG_ID
    responses.get(CALENDAR_URL, body=load_fixture("kalender.json").encode())

    result = await client.get_calendar_events(2025)

    assert result[0].waste_type is WasteType.GFT  # 129 → GFT
    assert result[1].waste_type is WasteType.RESIDUAL_WASTE  # 491 → RESIDUAL_WASTE
    assert result[5].waste_type is WasteType.CHRISTMAS_TREES  # 727 → CHRISTMAS_TREES


async def test_external_session_not_closed(responses: aioresponses) -> None:
    """Test that an externally supplied session is not closed by the client."""
    external_session = aiohttp.ClientSession()
    try:
        responses.get(ADDRESS_URL, payload=load_fixture_json("address.json"))
        responses.get(CALENDAR_URL, body=load_fixture("kalender.json").encode())
        async with CyclusClient(session=external_session) as client:
            await client.get_bag_id(ZIPCODE, HOUSE_NUMBER)
            await client.get_calendar_events(2025)

        assert not external_session.closed
    finally:
        await external_session.close()
