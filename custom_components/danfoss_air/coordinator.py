"""DataUpdateCoordinator for Danfoss Air."""

from datetime import timedelta
import logging
from typing import Any

from pydanfossair.commands import ReadCommand
from pydanfossair.danfossclient import DanfossClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(seconds=60)


class DanfossAirCoordinator(DataUpdateCoordinator[dict[ReadCommand, Any]]):
    """Coordinator for Danfoss Air CCM polling."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )
        self.host: str = entry.data[CONF_HOST]
        self._client = DanfossClient(self.host)

    async def _async_update_data(self) -> dict[ReadCommand, Any]:
        """Fetch data from the CCM unit."""
        try:
            return await self.hass.async_add_executor_job(self._fetch)
        except Exception as err:
            raise UpdateFailed(
                f"Error communicating with Danfoss Air CCM at {self.host}: {err}"
            ) from err

    def _fetch(self) -> dict[ReadCommand, Any]:
        """Synchronously fetch all data from the CCM unit."""
        c = self._client.command
        return {
            ReadCommand.exhaustTemperature: c(ReadCommand.exhaustTemperature),
            ReadCommand.outdoorTemperature: c(ReadCommand.outdoorTemperature),
            ReadCommand.supplyTemperature: c(ReadCommand.supplyTemperature),
            ReadCommand.extractTemperature: c(ReadCommand.extractTemperature),
            ReadCommand.humidity: round(c(ReadCommand.humidity), 2),
            ReadCommand.filterPercent: round(c(ReadCommand.filterPercent), 2),
            ReadCommand.bypass: c(ReadCommand.bypass),
            ReadCommand.fan_step: c(ReadCommand.fan_step),
            ReadCommand.supply_fan_speed: c(ReadCommand.supply_fan_speed),
            ReadCommand.exhaust_fan_speed: c(ReadCommand.exhaust_fan_speed),
            ReadCommand.away_mode: c(ReadCommand.away_mode),
            ReadCommand.boost: c(ReadCommand.boost),
            ReadCommand.battery_percent: c(ReadCommand.battery_percent),
            ReadCommand.automatic_bypass: c(ReadCommand.automatic_bypass),
            ReadCommand.roomTemperature: c(ReadCommand.roomTemperature),
            ReadCommand.roomTemperatureCalculated: c(ReadCommand.roomTemperatureCalculated),
            ReadCommand.operation_mode: c(ReadCommand.operation_mode),
        }

    async def async_send_command(self, command) -> Any:
        """Send a command to the CCM without updating cached data."""
        return await self.hass.async_add_executor_job(self._client.command, command)
