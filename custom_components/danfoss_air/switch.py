"""Support for the for Danfoss Air HRV switches."""

import logging
from typing import Any

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air switches from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DanfossAirSwitch(data, name, state_command, on_command, off_command)
        for name, state_command, on_command, off_command in _SWITCHES
    )


class DanfossAirSwitch(SwitchEntity):
    """Representation of a Danfoss Air switch."""

    _attr_has_entity_name = True

    def __init__(self, data, name, state_command, on_command, off_command):
        """Initialize the switch."""
        self._data = data
        self._state_command = state_command
        self._on_command = on_command
        self._off_command = off_command
        self._attr_name = name
        self._attr_unique_id = f"{data.host}_{state_command.name}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.host)},
            name="Danfoss Air",
            manufacturer="Danfoss",
            model="Air CCM",
        )

    def turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        _LOGGER.debug("Turning on switch with command %s", self._on_command)
        self._data.update_state(self._on_command, self._state_command)

    def turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        _LOGGER.debug("Turning off switch with command %s", self._off_command)
        self._data.update_state(self._off_command, self._state_command)

    def update(self) -> None:
        """Update the switch state."""
        self._data.update()
        self._attr_is_on = self._data.get_value(self._state_command)
        if self._attr_is_on is None:
            _LOGGER.debug("Could not get data for %s", self._state_command)
