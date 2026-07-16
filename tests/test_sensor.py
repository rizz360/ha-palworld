"""Tests for Palworld sensor entities."""
from __future__ import annotations

from homeassistant.helpers import entity_registry as er

from custom_components.palworld.const import DOMAIN
from custom_components.palworld.coordinator import PalworldData
from custom_components.palworld.sensor import SENSOR_DESCRIPTIONS

from .conftest import MOCK_INFO, MOCK_METRICS, MOCK_PLAYERS


def test_value_fn_derives_state_from_data():
    data = PalworldData(info=MOCK_INFO, metrics=MOCK_METRICS, players=MOCK_PLAYERS["players"])
    values = {desc.key: desc.value_fn(data) for desc in SENSOR_DESCRIPTIONS}

    assert values["server_fps"] == MOCK_METRICS["serverfps"]
    assert values["frame_time"] == MOCK_METRICS["serverframetime"]
    assert values["current_players"] == MOCK_METRICS["currentplayernum"]
    assert values["max_players"] == MOCK_METRICS["maxplayernum"]
    assert values["base_camps"] == MOCK_METRICS["basecampnum"]
    assert values["in_game_days"] == MOCK_METRICS["days"]
    assert values["uptime"] == MOCK_METRICS["uptime"]
    assert values["server_version"] == MOCK_INFO["version"]


def test_value_fn_returns_none_for_missing_metrics():
    data = PalworldData()

    for desc in SENSOR_DESCRIPTIONS:
        assert desc.value_fn(data) is None


def test_current_players_attributes_fn_lists_player_names():
    data = PalworldData(players=MOCK_PLAYERS["players"])
    desc = next(d for d in SENSOR_DESCRIPTIONS if d.key == "current_players")

    assert desc.attributes_fn(data) == {
        "players": [player["name"] for player in MOCK_PLAYERS["players"]]
    }


def test_only_current_players_defines_attributes_fn():
    for desc in SENSOR_DESCRIPTIONS:
        if desc.key != "current_players":
            assert desc.attributes_fn is None


def _entity_id(hass, config_entry, key: str) -> str | None:
    registry = er.async_get(hass)
    return registry.async_get_entity_id(
        "sensor", DOMAIN, f"{config_entry.entry_id}_{key}"
    )


async def test_sensors_are_registered_for_each_description(
    hass, setup_integration, mock_config_entry
):
    for desc in SENSOR_DESCRIPTIONS:
        entity_id = _entity_id(hass, mock_config_entry, desc.key)
        assert entity_id is not None
        assert hass.states.get(entity_id) is not None


async def test_server_fps_sensor_state(hass, setup_integration, mock_config_entry):
    entity_id = _entity_id(hass, mock_config_entry, "server_fps")

    state = hass.states.get(entity_id)

    assert state.state == str(MOCK_METRICS["serverfps"])


async def test_current_players_sensor_state_and_attributes(
    hass, setup_integration, mock_config_entry
):
    entity_id = _entity_id(hass, mock_config_entry, "current_players")

    state = hass.states.get(entity_id)

    assert state.state == str(MOCK_METRICS["currentplayernum"])
    assert state.attributes["players"] == [
        player["name"] for player in MOCK_PLAYERS["players"]
    ]
