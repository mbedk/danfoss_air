"""Support for Danfoss Air HRV fan step control."""

import logging

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

_FAN_STEP_COMMANDS = {
    1: UpdateCommand.set_fan_step_1,
    2: UpdateCommand.set_fan_step_2,
    3: UpdateCommand.set_fan_step_3,
    4: UpdateCommand.set_fan_step_4,
    5: UpdateCommand.set_fan_step_5,
    6: UpdateCommand.set_fan_step_6,
    7: UpdateCommand.set_fan_step_7,
    8: UpdateCommand.set_fan_step_8,
    9: UpdateCommand.set_fan_step_9,
    10: UpdateCommand.set_fan_step_10,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air number entities from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([DanfossAirFanStep(data)])


class DanfossAirFanStep(NumberEntity):
    """Representation of the Danfoss Air fan step control."""

    _attr_has_entity_name = True
    _attr_name = "Fan Step"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, data) -> None:
        """Initialize the fan step number entity."""
        self._data = data
        self._attr_unique_id = f"{data.host}_fan_step"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.host)},
            name="Danfoss Air",
            manufacturer="Danfoss",
            model="Air CCM",
        )

    def set_native_value(self, value: float) -> None:
        """Set the fan step on the Danfoss Air unit."""
        step = int(value)
        command = _FAN_STEP_COMMANDS.get(step)
        if command is None:
            _LOGGER.error("Invalid fan step value: %s", step)
            return
        _LOGGER.debug("Setting fan step to %s", step)
        self._data.send_command(command)
        self._attr_native_value = step

    def update(self) -> None:
        """Fetch the current fan step from the Danfoss Air unit."""
        self._data.update()
        raw = self._data.get_value(ReadCommand.fan_step)
        if raw is None:
            _LOGGER.debug("Could not get fan step data")
        else:
            self._attr_native_value = raw / 10
