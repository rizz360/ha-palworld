"""Thin async client for the Palworld dedicated server REST API.

API reference: docs/api.md (mirrors https://docs.palworldgame.com/category/rest-api)
"""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

from .const import LOGGER

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=10)


class PalworldApiError(Exception):
    """Base error for all Palworld API failures."""


class PalworldAuthError(PalworldApiError):
    """Raised on HTTP 401 (bad admin password)."""


class PalworldConnectionError(PalworldApiError):
    """Raised when the server can't be reached at all."""


class PalworldClient:
    """Wraps the Palworld REST API (Basic Auth, JSON in/out)."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        port: int,
        password: str,
        username: str = "admin",
    ) -> None:
        self._session = session
        self._base_url = f"http://{host}:{port}/v1/api"
        self._auth = aiohttp.BasicAuth(username, password)

    async def _request(
        self, method: str, path: str, json: dict[str, Any] | None = None
    ) -> Any:
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method,
                url,
                json=json,
                auth=self._auth,
                timeout=REQUEST_TIMEOUT,
            ) as resp:
                if resp.status == 401:
                    raise PalworldAuthError("Invalid admin password")
                if resp.status >= 400:
                    body = await resp.text()
                    raise PalworldApiError(
                        f"{method} {path} failed with HTTP {resp.status}: {body}"
                    )
                if resp.content_type == "application/json":
                    return await resp.json()
                return await resp.text()
        except asyncio.TimeoutError as err:
            raise PalworldConnectionError(f"Timed out calling {path}") from err
        except aiohttp.ClientError as err:
            raise PalworldConnectionError(f"Error calling {path}: {err}") from err

    # -- Read endpoints ----------------------------------------------------

    async def get_info(self) -> dict[str, Any]:
        return await self._request("GET", "/info")

    async def get_players(self) -> dict[str, Any]:
        return await self._request("GET", "/players")

    async def get_settings(self) -> dict[str, Any]:
        return await self._request("GET", "/settings")

    async def get_metrics(self) -> dict[str, Any]:
        return await self._request("GET", "/metrics")

    async def get_game_data(self) -> dict[str, Any]:
        return await self._request("GET", "/game-data")

    # -- Action endpoints ----------------------------------------------------

    async def announce(self, message: str) -> None:
        await self._request("POST", "/announce", json={"message": message})

    async def kick(self, userid: str, message: str = "") -> None:
        await self._request(
            "POST", "/kick", json={"userid": userid, "message": message}
        )

    async def ban(self, userid: str, message: str = "") -> None:
        await self._request(
            "POST", "/ban", json={"userid": userid, "message": message}
        )

    async def unban(self, userid: str) -> None:
        await self._request("POST", "/unban", json={"userid": userid})

    async def save(self) -> None:
        await self._request("POST", "/save")

    async def shutdown(self, waittime: int, message: str = "") -> None:
        await self._request(
            "POST", "/shutdown", json={"waittime": waittime, "message": message}
        )

    async def stop(self) -> None:
        await self._request("POST", "/stop")

    async def async_validate(self) -> dict[str, Any]:
        """Validate connectivity/credentials by fetching /info."""
        LOGGER.debug("Validating Palworld connection to %s", self._base_url)
        return await self.get_info()
