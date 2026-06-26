"""Support for Danfoss Air HRV fan step control."""

import logging

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

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
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air number entities."""
    async_add_entities([DanfossAirFanStep(entry.runtime_data)])


class DanfossAirFanStep(DanfossAirEntity, NumberEntity):
    """Representation of the Danfoss Air fan step control."""

    _attr_translation_key = "fan_step"
    _attr_native_min_value = 1
    _attr_native_max_value = 10
    _attr_native_step = 1
    _attr_mode = NumberMode.SLIDER

    def __init__(self, coordinator) -> None:
        """Initialize the fan step number entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_fan_step"

    @property
    def native_value(self) -> float | None:
        """Return the current fan step (1–10)."""
        raw = self.coordinator.data.get(ReadCommand.fan_step)
        if raw is None:
            return None
        return raw / 10

    async def async_set_native_value(self, value: float) -> None:
        """Set the fan step on the Danfoss Air unit."""
        step = int(value)
        command = _FAN_STEP_COMMANDS.get(step)
        if command is None:
            _LOGGER.error("Invalid fan step value: %s", step)
            return
        _LOGGER.debug("Setting fan step to %s", step)
        await self.coordinator.async_send_command(command)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, ReadCommand.fan_step: step * 10}
        )
