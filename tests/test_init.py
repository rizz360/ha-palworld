"""Tests for integration setup, unload, and the registered services."""
from __future__ import annotations

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import device_registry as dr

from custom_components.palworld.api import PalworldApiError
from custom_components.palworld.const import (
    DOMAIN,
    SERVICE_ANNOUNCE,
    SERVICE_BAN,
    SERVICE_KICK,
    SERVICE_SAVE,
    SERVICE_SHUTDOWN,
    SERVICE_STOP,
    SERVICE_UNBAN,
)


async def _device_id(hass, config_entry) -> str:
    registry = dr.async_get(hass)
    device = registry.async_get_device(identifiers={(DOMAIN, config_entry.entry_id)})
    assert device is not None
    return device.id


async def test_setup_and_unload_entry(hass, setup_integration, mock_config_entry):
    assert mock_config_entry.state is ConfigEntryState.LOADED
    assert hass.services.has_service(DOMAIN, SERVICE_SAVE)

    assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
    assert not hass.services.has_service(DOMAIN, SERVICE_SAVE)


async def test_service_save(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN, SERVICE_SAVE, {"device_id": device_id}, blocking=True
    )

    setup_integration.save.assert_called_once()


async def test_service_announce(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_ANNOUNCE,
        {"device_id": device_id, "message": "hi everyone"},
        blocking=True,
    )

    setup_integration.announce.assert_called_once_with("hi everyone")


async def test_service_kick(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_KICK,
        {"device_id": device_id, "userid": "steam_1", "message": "bye"},
        blocking=True,
    )

    setup_integration.kick.assert_called_once_with("steam_1", "bye")


async def test_service_kick_defaults_message_to_empty_string(
    hass, setup_integration, mock_config_entry
):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_KICK,
        {"device_id": device_id, "userid": "steam_1"},
        blocking=True,
    )

    setup_integration.kick.assert_called_once_with("steam_1", "")


async def test_service_ban(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_BAN,
        {"device_id": device_id, "userid": "steam_1", "message": "bad actor"},
        blocking=True,
    )

    setup_integration.ban.assert_called_once_with("steam_1", "bad actor")


async def test_service_unban(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_UNBAN,
        {"device_id": device_id, "userid": "steam_1"},
        blocking=True,
    )

    setup_integration.unban.assert_called_once_with("steam_1")


async def test_service_shutdown(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN,
        SERVICE_SHUTDOWN,
        {"device_id": device_id, "waittime": 30, "message": "restarting"},
        blocking=True,
    )

    setup_integration.shutdown.assert_called_once_with(30, "restarting")


async def test_service_stop(hass, setup_integration, mock_config_entry):
    device_id = await _device_id(hass, mock_config_entry)

    await hass.services.async_call(
        DOMAIN, SERVICE_STOP, {"device_id": device_id}, blocking=True
    )

    setup_integration.stop.assert_called_once()


async def test_service_unknown_device_raises(hass, setup_integration):
    with pytest.raises(HomeAssistantError, match="Unknown device_id"):
        await hass.services.async_call(
            DOMAIN, SERVICE_SAVE, {"device_id": "not-a-real-device"}, blocking=True
        )


async def test_service_wraps_api_error_as_hass_error(
    hass, setup_integration, mock_config_entry
):
    device_id = await _device_id(hass, mock_config_entry)
    setup_integration.save.side_effect = PalworldApiError("boom")

    with pytest.raises(HomeAssistantError, match="boom"):
        await hass.services.async_call(
            DOMAIN, SERVICE_SAVE, {"device_id": device_id}, blocking=True
        )
