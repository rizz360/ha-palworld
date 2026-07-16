"""Tests for Palworld button entities."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from custom_components.palworld.api import PalworldApiError
from custom_components.palworld.button import BUTTON_DESCRIPTIONS
from custom_components.palworld.const import DOMAIN


async def test_save_world_press_fn_calls_client_save():
    client = AsyncMock()
    desc = next(d for d in BUTTON_DESCRIPTIONS if d.key == "save_world")

    await desc.press_fn(client)

    client.save.assert_called_once()


async def test_force_stop_press_fn_calls_client_stop():
    client = AsyncMock()
    desc = next(d for d in BUTTON_DESCRIPTIONS if d.key == "force_stop")

    await desc.press_fn(client)

    client.stop.assert_called_once()


def test_force_stop_is_disabled_by_default():
    desc = next(d for d in BUTTON_DESCRIPTIONS if d.key == "force_stop")
    assert desc.entity_registry_enabled_default is False


def _entity_id(hass, config_entry, key: str) -> str | None:
    registry = er.async_get(hass)
    return registry.async_get_entity_id(
        "button", DOMAIN, f"{config_entry.entry_id}_{key}"
    )


async def test_buttons_are_registered_for_each_description(
    hass, setup_integration, mock_config_entry
):
    for desc in BUTTON_DESCRIPTIONS:
        assert _entity_id(hass, mock_config_entry, desc.key) is not None


async def test_save_world_button_press_calls_client(
    hass, setup_integration, mock_config_entry
):
    entity_id = _entity_id(hass, mock_config_entry, "save_world")

    await hass.services.async_call(
        "button", "press", {"entity_id": entity_id}, blocking=True
    )

    setup_integration.save.assert_called_once()


async def test_button_press_wraps_api_error_as_hass_error(
    hass, setup_integration, mock_config_entry
):
    entity_id = _entity_id(hass, mock_config_entry, "save_world")
    setup_integration.save.side_effect = PalworldApiError("boom")

    with pytest.raises(HomeAssistantError, match="boom"):
        await hass.services.async_call(
            "button", "press", {"entity_id": entity_id}, blocking=True
        )
