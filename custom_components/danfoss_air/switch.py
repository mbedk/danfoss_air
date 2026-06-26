"""Support for Danfoss Air HRV switches."""

import logging
from typing import Any

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

_SWITCHES = [
    (
        "Boost",
        ReadCommand.boost,
        UpdateCommand.boost_activate,
        UpdateCommand.boost_deactivate,
    ),
    (
        "Bypass",
        ReadCommand.bypass,
        UpdateCommand.bypass_activate,
        UpdateCommand.bypass_deactivate,
    ),
    (
        "Automatic Bypass",
        ReadCommand.automatic_bypass,
        UpdateCommand.bypass_activate,
        UpdateCommand.bypass_deactivate,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air switches."""
    async_add_entities(
        DanfossAirSwitch(entry.runtime_data, name, state_cmd, on_cmd, off_cmd)
        for name, state_cmd, on_cmd, off_cmd in _SWITCHES
    )


class DanfossAirSwitch(DanfossAirEntity, SwitchEntity):
    """Representation of a Danfoss Air switch."""

    def __init__(self, coordinator, name, state_command, on_command, off_command):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._state_command = state_command
        self._on_command = on_command
        self._off_command = off_command
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{state_command.name}"

    @property
    def is_on(self) -> bool | None:
        """Return the switch state."""
        return self.coordinator.data.get(self._state_command)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on %s", self._attr_name)
        result = await self.coordinator.async_send_command(self._on_command)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._state_command: result}
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off %s", self._attr_name)
        result = await self.coordinator.async_send_command(self._off_command)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._state_command: result}
        )
