"""Asynchronous Python client for Cyclus NV."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Self
from urllib.parse import unquote

import aiohttp
from aiohttp.hdrs import METH_GET, METH_POST
from mashumaro.codecs.orjson import ORJSONDecoder
from yarl import URL

from cyclus.const import HOST
from cyclus.exceptions import CyclusError
from cyclus.models import Address, CalendarEvent, WasteRegistration

_BASE_URL = URL(f"https://{HOST}")


@dataclass
class CyclusClient:
    """Main class for handling connections with the Cyclus NV API."""

    bag_id: str | None = None
    session: aiohttp.ClientSession | None = None
    request_timeout: int = 10
    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        json: dict[str, str | int] | None = None,
        headers: dict[str, str] | None = None,
    ) -> str:
        """Handle a request to the Cyclus NV API."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        url = _BASE_URL / uri
        async with asyncio.timeout(self.request_timeout):
            async with self.session.request(
                method,
                url,
                json=json,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                return await resp.text()

    async def _ensure_csrf(self) -> str:
        """Seed the cookie jar and return the XSRF token."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        async with asyncio.timeout(self.request_timeout):
            async with self.session.get(_BASE_URL) as resp:
                resp.raise_for_status()

        xsrf_cookie = self.session.cookie_jar.filter_cookies(_BASE_URL).get(
            "XSRF-TOKEN"
        )
        if xsrf_cookie is None:
            msg = "XSRF-TOKEN cookie not found after loading home page"
            raise CyclusError(msg)
        return unquote(xsrf_cookie.value)

    async def _post(self, uri: str, payload: dict[str, str | int]) -> str:
        """Handle a POST request to the Cyclus NV API."""
        xsrf_token = await self._ensure_csrf()
        return await self._request(
            uri,
            method=METH_POST,
            json=payload,
            headers={"X-XSRF-TOKEN": xsrf_token},
        )

    async def get_bag_id(self, zipcode: str, house_number: int) -> str:
        """Fetch and store the BAG ID for the given address."""
        result = await self._request(f"adressen/{zipcode}:{house_number}")
        addresses = ORJSONDecoder(list[Address]).decode(result)
        if not addresses:
            msg = f"No address found for {zipcode} {house_number}"
            raise CyclusError(msg)
        self.bag_id = addresses[0].bag_id
        return self.bag_id

    async def get_waste_registrations(self, login_code: str) -> list[WasteRegistration]:
        """Retrieve waste registrations for the configured address."""
        if self.bag_id is None:
            msg = "No bag_id set. Call get_bag_id() first."
            raise CyclusError(msg)
        result = await self._post(
            "diftar/afvalregistraties", {"bag_id": self.bag_id, "code": login_code}
        )

        if result == "false":
            # The API returns false when no registrations have been made yet.
            return []

        return ORJSONDecoder(list[WasteRegistration]).decode(result)

    async def get_calendar_events(self, year: int) -> list[CalendarEvent]:
        """Retrieve the waste collection calendar for the configured address."""
        if self.bag_id is None:
            msg = "No bag_id set. Call get_bag_id() first."
            raise CyclusError(msg)
        result = await self._request(f"rest/adressen/{self.bag_id}/kalender/{year}")
        return ORJSONDecoder(list[CalendarEvent]).decode(result)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The CyclusClient object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
