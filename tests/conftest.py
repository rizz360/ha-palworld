"""Common fixtures and test data for the Palworld integration tests."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.palworld.const import DOMAIN

pytest_plugins = "pytest_homeassistant_custom_component"

MOCK_DATA = {
    "host": "127.0.0.1",
    "port": 8212,
    "username": "admin",
    "password": "s3cret",
}

MOCK_INFO = {"version": "v1.5.0", "servername": "My Palworld Server"}

MOCK_METRICS = {
    "serverfps": 60,
    "serverframetime": 16.6,
    "currentplayernum": 2,
    "maxplayernum": 32,
    "basecampnum": 3,
    "days": 12,
    "uptime": 3600,
}

MOCK_PLAYERS = {
    "players": [
        {"name": "Alice", "userId": "steam_1"},
        {"name": "Bob", "userId": "steam_2"},
    ]
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable loading of custom_components/palworld for every test."""
    yield


@pytest.fixture(autouse=True)
def mock_get_clientsession():
    """Never open a real aiohttp session/DNS resolver during tests.

    A real session pulls in aiohttp's AsyncResolver (pycares), whose shutdown
    thread races the test-cleanup check and makes the very first test that
    touches it flaky.
    """
    fake_session = MagicMock()
    with patch(
        "custom_components.palworld.async_get_clientsession",
        return_value=fake_session,
    ), patch(
        "custom_components.palworld.config_flow.async_get_clientsession",
        return_value=fake_session,
    ):
        yield


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """A config entry matching MOCK_DATA."""
    return MockConfigEntry(
        domain=DOMAIN,
        data=MOCK_DATA,
        unique_id=f"{MOCK_DATA['host']}:{MOCK_DATA['port']}",
    )


@pytest.fixture
def mock_client() -> AsyncMock:
    """A PalworldClient double with canned successful responses."""
    client = AsyncMock()
    client.get_info.return_value = MOCK_INFO
    client.get_metrics.return_value = MOCK_METRICS
    client.get_players.return_value = MOCK_PLAYERS
    client.async_validate.return_value = MOCK_INFO
    return client


@pytest.fixture
async def setup_integration(hass, mock_config_entry, mock_client):
    """Fully set up the integration with a mocked PalworldClient."""
    mock_config_entry.add_to_hass(hass)
    with patch(
        "custom_components.palworld.PalworldClient", return_value=mock_client
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
    return mock_client
