"""The Palworld Server integration."""
from __future__ import annotations

from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv, device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PalworldApiError, PalworldClient
from .const import (
    ATTR_MESSAGE,
    ATTR_USERID,
    ATTR_WAITTIME,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    SERVICE_ANNOUNCE,
    SERVICE_BAN,
    SERVICE_KICK,
    SERVICE_SAVE,
    SERVICE_SHUTDOWN,
    SERVICE_STOP,
    SERVICE_UNBAN,
)
from .coordinator import PalworldDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BUTTON]

SERVICE_DEVICE_SCHEMA = vol.Schema({vol.Required("device_id"): cv.string})
SERVICE_ANNOUNCE_SCHEMA = SERVICE_DEVICE_SCHEMA.extend(
    {vol.Required(ATTR_MESSAGE): cv.string}
)
SERVICE_PLAYER_SCHEMA = SERVICE_DEVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_USERID): cv.string,
        vol.Optional(ATTR_MESSAGE, default=""): cv.string,
    }
)
SERVICE_UNBAN_SCHEMA = SERVICE_DEVICE_SCHEMA.extend(
    {vol.Required(ATTR_USERID): cv.string}
)
SERVICE_SHUTDOWN_SCHEMA = SERVICE_DEVICE_SCHEMA.extend(
    {
        vol.Required(ATTR_WAITTIME): vol.All(vol.Coerce(int), vol.Range(min=0)),
        vol.Optional(ATTR_MESSAGE, default=""): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Palworld Server from a config entry."""
    session = async_get_clientsession(hass)
    client = PalworldClient(
        session,
        host=entry.data[CONF_HOST],
        port=entry.data[CONF_PORT],
        password=entry.data[CONF_PASSWORD],
        username=entry.data.get(CONF_USERNAME, DEFAULT_USERNAME),
    )

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = PalworldDataUpdateCoordinator(
        hass, entry, client, timedelta(seconds=scan_interval)
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    _async_register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
            for service in (
                SERVICE_ANNOUNCE,
                SERVICE_KICK,
                SERVICE_BAN,
                SERVICE_UNBAN,
                SERVICE_SAVE,
                SERVICE_SHUTDOWN,
                SERVICE_STOP,
            ):
                hass.services.async_remove(DOMAIN, service)
    return unloaded


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _coordinator_for_device(
    hass: HomeAssistant, device_id: str
) -> PalworldDataUpdateCoordinator:
    device = dr.async_get(hass).async_get(device_id)
    if device is None:
        raise HomeAssistantError(f"Unknown device_id: {device_id}")
    for entry_id in device.config_entries:
        if entry_id in hass.data.get(DOMAIN, {}):
            return hass.data[DOMAIN][entry_id]
    raise HomeAssistantError(f"Device {device_id} is not a Palworld Server")


def _async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_SAVE):
        return

    async def _handle_announce(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.announce(call.data[ATTR_MESSAGE])
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_kick(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.kick(
                call.data[ATTR_USERID], call.data[ATTR_MESSAGE]
            )
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_ban(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.ban(
                call.data[ATTR_USERID], call.data[ATTR_MESSAGE]
            )
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_unban(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.unban(call.data[ATTR_USERID])
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_save(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.save()
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_shutdown(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.shutdown(
                call.data[ATTR_WAITTIME], call.data[ATTR_MESSAGE]
            )
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    async def _handle_stop(call: ServiceCall) -> None:
        coordinator = _coordinator_for_device(hass, call.data["device_id"])
        try:
            await coordinator.client.stop()
        except PalworldApiError as err:
            raise HomeAssistantError(str(err)) from err

    hass.services.async_register(
        DOMAIN, SERVICE_ANNOUNCE, _handle_announce, schema=SERVICE_ANNOUNCE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_KICK, _handle_kick, schema=SERVICE_PLAYER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_BAN, _handle_ban, schema=SERVICE_PLAYER_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_UNBAN, _handle_unban, schema=SERVICE_UNBAN_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SAVE, _handle_save, schema=SERVICE_DEVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SHUTDOWN, _handle_shutdown, schema=SERVICE_SHUTDOWN_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP, _handle_stop, schema=SERVICE_DEVICE_SCHEMA
    )
