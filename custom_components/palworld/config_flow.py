"""Config flow for the Palworld Server integration."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import PalworldApiError, PalworldAuthError, PalworldClient, PalworldConnectionError
from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
    LOGGER,
    MIN_SCAN_INTERVAL,
)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Optional(CONF_USERNAME, default=DEFAULT_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def _validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the connection info by calling /info. Raises on failure."""
    session = async_get_clientsession(hass)
    client = PalworldClient(
        session,
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        password=data[CONF_PASSWORD],
        username=data.get(CONF_USERNAME, DEFAULT_USERNAME),
    )
    info = await client.async_validate()
    return {"title": info.get("servername") or f"Palworld ({data[CONF_HOST]})"}


class PalworldConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Palworld Server."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]}
            )
            try:
                info = await _validate_input(self.hass, user_input)
            except PalworldAuthError:
                errors["base"] = "invalid_auth"
            except PalworldConnectionError:
                errors["base"] = "cannot_connect"
            except PalworldApiError:
                errors["base"] = "unknown"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error validating Palworld connection")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> PalworldOptionsFlow:
        return PalworldOptionsFlow()


class PalworldOptionsFlow(OptionsFlow):
    """Handle Palworld options (polling interval)."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_SCAN_INTERVAL, default=current): vol.All(
                    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)
                )
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
