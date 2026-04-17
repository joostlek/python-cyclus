"""Asynchronous Python client for Cyclus NV."""

from collections.abc import AsyncGenerator, Generator

import aiohttp
from aioresponses import aioresponses
import pytest
from yarl import URL

from cyclus import CyclusClient
from cyclus.const import HOST
from syrupy import SnapshotAssertion
from tests.const import XSRF_TOKEN
from tests.syrupy import CyclusSnapshotExtension


@pytest.fixture(name="snapshot")
def snapshot_assertion(snapshot: SnapshotAssertion) -> SnapshotAssertion:
    """Return snapshot assertion fixture with the Cyclus extension."""
    return snapshot.use_extension(CyclusSnapshotExtension)


@pytest.fixture
async def client() -> AsyncGenerator[CyclusClient, None]:
    """Return a Cyclus client."""
    session = aiohttp.ClientSession()
    session.cookie_jar.update_cookies(
        {"XSRF-TOKEN": XSRF_TOKEN}, URL(f"https://{HOST}")
    )
    async with CyclusClient(session=session) as cyclus_client:
        yield cyclus_client
    await session.close()


@pytest.fixture(name="responses")
def aioresponses_fixture() -> Generator[aioresponses, None, None]:
    """Return aioresponses fixture."""
    with aioresponses() as mocked_responses:
        yield mocked_responses
