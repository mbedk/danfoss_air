"""Support for Danfoss Air HRV fan step control."""

import logging

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from . import DOMAIN

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


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Danfoss Air number platform."""
    data = hass.data[DOMAIN]
    add_entities([DanfossAirFanStep(data)], True)


class DanfossAirFanStep(NumberEntity):
    """Representation of the Danfoss Air fan step control."""

    _attr_name = "Danfoss Air Fan Step"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, data) -> None:
        """Initialize the fan step number entity."""
        self._data = data

    def set_native_value(self, value: float) -> None:
        """Set the fan step on the Danfoss Air unit."""
        step = int(value)
        command = _FAN_STEP_COMMANDS.get(step)
        if command is None:
            _LOGGER.error("Invalid fan step value: %s", step)
            return
        _LOGGER.debug("Setting fan step to %s", step)
        self._data.update_state(command, ReadCommand.fan_step)
        self._attr_native_value = step

    def update(self) -> None:
        """Fetch the current fan step from the Danfoss Air unit."""
        self._data.update()
        raw = self._data.get_value(ReadCommand.fan_step)
        if raw is None:
            _LOGGER.debug("Could not get fan step data")
        else:
            self._attr_native_value = raw / 10
