"""Sensors for the Palworld Server integration."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import PalworldData, PalworldDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class PalworldSensorEntityDescription(SensorEntityDescription):
    """Describes a Palworld sensor entity."""

    value_fn: Callable[[PalworldData], StateType]
    attributes_fn: Callable[[PalworldData], dict[str, Any]] | None = None


SENSOR_DESCRIPTIONS: tuple[PalworldSensorEntityDescription, ...] = (
    PalworldSensorEntityDescription(
        key="server_fps",
        translation_key="server_fps",
        icon="mdi:speedometer",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.metrics.get("serverfps"),
    ),
    PalworldSensorEntityDescription(
        key="frame_time",
        translation_key="frame_time",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.metrics.get("serverframetime"),
    ),
    PalworldSensorEntityDescription(
        key="current_players",
        translation_key="current_players",
        icon="mdi:account-multiple",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.metrics.get("currentplayernum"),
        attributes_fn=lambda data: {
            "players": [player.get("name") for player in data.players]
        },
    ),
    PalworldSensorEntityDescription(
        key="max_players",
        translation_key="max_players",
        icon="mdi:account-multiple-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.metrics.get("maxplayernum"),
    ),
    PalworldSensorEntityDescription(
        key="base_camps",
        translation_key="base_camps",
        icon="mdi:home-group",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.metrics.get("basecampnum"),
    ),
    PalworldSensorEntityDescription(
        key="in_game_days",
        translation_key="in_game_days",
        icon="mdi:calendar-clock",
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.metrics.get("days"),
    ),
    PalworldSensorEntityDescription(
        key="uptime",
        translation_key="uptime",
        icon="mdi:clock-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.metrics.get("uptime"),
    ),
    PalworldSensorEntityDescription(
        key="server_version",
        translation_key="server_version",
        icon="mdi:tag-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.info.get("version"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Palworld sensors from a config entry."""
    coordinator: PalworldDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PalworldSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class PalworldSensor(CoordinatorEntity[PalworldDataUpdateCoordinator], SensorEntity):
    """A single Palworld server metric/info sensor."""

    entity_description: PalworldSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PalworldDataUpdateCoordinator,
        entry: ConfigEntry,
        description: PalworldSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
            sw_version=coordinator.data.info.get("version") if coordinator.data else None,
        )

    @property
    def native_value(self) -> StateType:
        return self.entity_description.value_fn(self.coordinator.data)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        if self.entity_description.attributes_fn is None:
            return None
        return self.entity_description.attributes_fn(self.coordinator.data)
