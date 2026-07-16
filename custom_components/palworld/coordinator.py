"""Data update coordinator for the Palworld Server integration."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PalworldApiError, PalworldAuthError, PalworldClient
from .const import DOMAIN, LOGGER


@dataclass
class PalworldData:
    """Aggregated data polled from the Palworld server."""

    info: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)
    players: list[dict[str, Any]] = field(default_factory=list)


class PalworldDataUpdateCoordinator(DataUpdateCoordinator[PalworldData]):
    """Polls /info, /metrics and /players on a fixed interval."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        client: PalworldClient,
        update_interval: timedelta,
    ) -> None:
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.client = client

    async def _async_update_data(self) -> PalworldData:
        try:
            info, metrics, players = await asyncio.gather(
                self.client.get_info(),
                self.client.get_metrics(),
                self.client.get_players(),
            )
        except PalworldAuthError as err:
            raise ConfigEntryAuthFailed("Invalid admin password") from err
        except PalworldApiError as err:
            raise UpdateFailed(str(err)) from err

        return PalworldData(
            info=info,
            metrics=metrics,
            players=players.get("players", []),
        )
