"""Buttons for the Palworld Server integration."""
from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import PalworldApiError, PalworldClient
from .const import DOMAIN, MANUFACTURER, MODEL
from .coordinator import PalworldDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class PalworldButtonEntityDescription(ButtonEntityDescription):
    """Describes a Palworld button entity."""

    press_fn: Callable[[PalworldClient], Coroutine[Any, Any, None]]


BUTTON_DESCRIPTIONS: tuple[PalworldButtonEntityDescription, ...] = (
    PalworldButtonEntityDescription(
        key="save_world",
        translation_key="save_world",
        icon="mdi:content-save",
        press_fn=lambda client: client.save(),
    ),
    PalworldButtonEntityDescription(
        key="force_stop",
        translation_key="force_stop",
        icon="mdi:stop-circle-outline",
        entity_registry_enabled_default=False,
        press_fn=lambda client: client.stop(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Palworld buttons from a config entry."""
    coordinator: PalworldDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PalworldButton(coordinator, entry, description)
        for description in BUTTON_DESCRIPTIONS
    )


class PalworldButton(CoordinatorEntity[PalworldDataUpdateCoordinator], ButtonEntity):
    """A Palworld server action button."""

    entity_description: PalworldButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: PalworldDataUpdateCoordinator,
        entry: ConfigEntry,
        description: PalworldButtonEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    async def async_press(self) -> None:
        try:
            await self.entity_description.press_fn(self.coordinator.client)
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err
