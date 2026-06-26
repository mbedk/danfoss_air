"""Support for Danfoss Air HRV sensors."""

import logging

from pydanfossair.commands import ReadCommand

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

_SENSORS = [
    (
        "Exhaust Temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.exhaustTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "Outdoor Temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.outdoorTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "Supply Temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.supplyTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "Extract Temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.extractTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "Remaining Filter",
        PERCENTAGE,
        ReadCommand.filterPercent,
        None,
        None,
    ),
    (
        "Humidity",
        PERCENTAGE,
        ReadCommand.humidity,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
    ),
    (
        "Exhaust Fan Speed",
        REVOLUTIONS_PER_MINUTE,
        ReadCommand.exhaust_fan_speed,
        None,
        None,
    ),
    (
        "Supply Fan Speed",
        REVOLUTIONS_PER_MINUTE,
        ReadCommand.supply_fan_speed,
        None,
        None,
    ),
    (
        "Dial Battery",
        PERCENTAGE,
        ReadCommand.battery_percent,
        SensorDeviceClass.BATTERY,
        None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air sensors."""
    async_add_entities(
        DanfossAirSensor(entry.runtime_data, name, unit, command, device_class, state_class)
        for name, unit, command, device_class, state_class in _SENSORS
    )


class DanfossAirSensor(DanfossAirEntity, SensorEntity):
    """Representation of a Danfoss Air sensor."""

    def __init__(self, coordinator, name, unit, command, device_class, state_class):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._command = command
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{command.name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the sensor value."""
        return self.coordinator.data.get(self._command)
