"""Tests for the Palworld REST API client."""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

from custom_components.palworld.api import (
    PalworldApiError,
    PalworldAuthError,
    PalworldClient,
    PalworldConnectionError,
)


def _make_session(
    *,
    status: int = 200,
    json_data=None,
    text_data: str = "",
    content_type: str = "application/json",
    side_effect: Exception | None = None,
):
    """Build a mock aiohttp.ClientSession whose request() yields a canned response."""
    response = MagicMock()
    response.status = status
    response.content_type = content_type
    response.json = AsyncMock(return_value=json_data)
    response.text = AsyncMock(return_value=text_data)

    @asynccontextmanager
    async def _request(*args, **kwargs):
        if side_effect is not None:
            raise side_effect
        yield response

    session = MagicMock(spec=aiohttp.ClientSession)
    session.request = MagicMock(side_effect=_request)
    return session, response


@pytest.fixture
def client_factory():
    def _factory(session) -> PalworldClient:
        return PalworldClient(session, host="127.0.0.1", port=8212, password="secret")

    return _factory


async def test_get_info_success(client_factory):
    session, _ = _make_session(json_data={"version": "v1.5.0"})
    client = client_factory(session)

    result = await client.get_info()

    assert result == {"version": "v1.5.0"}
    args, kwargs = session.request.call_args
    assert args[0] == "GET"
    assert args[1] == "http://127.0.0.1:8212/v1/api/info"
    assert kwargs["auth"].login == "admin"
    assert kwargs["auth"].password == "secret"


async def test_request_raises_auth_error_on_401(client_factory):
    session, _ = _make_session(status=401)
    client = client_factory(session)

    with pytest.raises(PalworldAuthError):
        await client.get_info()


async def test_request_raises_api_error_on_http_error(client_factory):
    session, _ = _make_session(status=500, text_data="boom")
    client = client_factory(session)

    with pytest.raises(PalworldApiError, match="HTTP 500"):
        await client.get_players()


async def test_request_raises_connection_error_on_timeout(client_factory):
    session, _ = _make_session(side_effect=asyncio.TimeoutError())
    client = client_factory(session)

    with pytest.raises(PalworldConnectionError):
        await client.get_info()


async def test_request_raises_connection_error_on_client_error(client_factory):
    session, _ = _make_session(side_effect=aiohttp.ClientConnectionError())
    client = client_factory(session)

    with pytest.raises(PalworldConnectionError):
        await client.get_info()


async def test_request_returns_text_when_not_json(client_factory):
    session, _ = _make_session(content_type="text/plain", text_data="pong")
    client = client_factory(session)

    result = await client.get_info()

    assert result == "pong"


async def test_announce_sends_message_payload(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.announce("hello")

    _, kwargs = session.request.call_args
    assert kwargs["json"] == {"message": "hello"}


async def test_kick_sends_userid_and_message(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.kick("steam_1", "bye")

    _, kwargs = session.request.call_args
    assert kwargs["json"] == {"userid": "steam_1", "message": "bye"}


async def test_ban_sends_userid_and_message(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.ban("steam_1", "bad actor")

    _, kwargs = session.request.call_args
    assert kwargs["json"] == {"userid": "steam_1", "message": "bad actor"}


async def test_unban_sends_userid(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.unban("steam_1")

    _, kwargs = session.request.call_args
    assert kwargs["json"] == {"userid": "steam_1"}


async def test_shutdown_sends_waittime_and_message(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.shutdown(30, "restarting")

    _, kwargs = session.request.call_args
    assert kwargs["json"] == {"waittime": 30, "message": "restarting"}


async def test_save_and_stop_send_no_payload(client_factory):
    session, _ = _make_session(json_data={})
    client = client_factory(session)

    await client.save()
    assert session.request.call_args.kwargs["json"] is None

    await client.stop()
    assert session.request.call_args.kwargs["json"] is None


async def test_async_validate_calls_get_info(client_factory):
    session, _ = _make_session(json_data={"version": "v1.5.0"})
    client = client_factory(session)

    result = await client.async_validate()

    assert result == {"version": "v1.5.0"}
    assert session.request.call_args.args[1] == "http://127.0.0.1:8212/v1/api/info"
