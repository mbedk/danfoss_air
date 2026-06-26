"""Support for Danfoss Air HRV binary sensors."""

from pydanfossair.commands import ReadCommand

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

PARALLEL_UPDATES = 0

_SENSORS = [
    ("Bypass Active", ReadCommand.bypass, BinarySensorDeviceClass.OPENING),
    ("Away Mode Active", ReadCommand.away_mode, None),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air binary sensors."""
    async_add_entities(
        DanfossAirBinarySensor(entry.runtime_data, name, command, device_class)
        for name, command, device_class in _SENSORS
    )


class DanfossAirBinarySensor(DanfossAirEntity, BinarySensorEntity):
    """Representation of a Danfoss Air binary sensor."""

    def __init__(self, coordinator, name, command, device_class):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._command = command
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{command.name}"
        self._attr_device_class = device_class

    @property
    def is_on(self):
        """Return the binary sensor state."""
        return self.coordinator.data.get(self._command)
