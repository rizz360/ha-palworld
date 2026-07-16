"""Tests for the Palworld data update coordinator."""
from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.palworld.api import PalworldApiError, PalworldAuthError
from custom_components.palworld.coordinator import PalworldDataUpdateCoordinator

from .conftest import MOCK_INFO, MOCK_METRICS, MOCK_PLAYERS


@pytest.fixture
def coordinator(hass, mock_config_entry, mock_client) -> PalworldDataUpdateCoordinator:
    mock_config_entry.add_to_hass(hass)
    return PalworldDataUpdateCoordinator(
        hass, mock_config_entry, mock_client, timedelta(seconds=30)
    )


async def test_update_data_success(coordinator):
    data = await coordinator._async_update_data()

    assert data.info == MOCK_INFO
    assert data.metrics == MOCK_METRICS
    assert data.players == MOCK_PLAYERS["players"]


async def test_update_data_auth_error_raises_config_entry_auth_failed(coordinator):
    coordinator.client.get_info.side_effect = PalworldAuthError()

    with pytest.raises(ConfigEntryAuthFailed):
        await coordinator._async_update_data()


async def test_update_data_api_error_raises_update_failed(coordinator):
    coordinator.client.get_players.side_effect = PalworldApiError("boom")

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_update_data_players_defaults_to_empty_list(coordinator):
    coordinator.client.get_players.return_value = {}

    data = await coordinator._async_update_data()

    assert data.players == []
