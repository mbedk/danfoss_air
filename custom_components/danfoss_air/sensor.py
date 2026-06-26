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
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0

_SENSORS = [
    (
        "exhaust_temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.exhaustTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        True,
    ),
    (
        "outdoor_temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.outdoorTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        True,
    ),
    (
        "supply_temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.supplyTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        True,
    ),
    (
        "extract_temperature",
        UnitOfTemperature.CELSIUS,
        ReadCommand.extractTemperature,
        SensorDeviceClass.TEMPERATURE,
        SensorStateClass.MEASUREMENT,
        None,
        True,
    ),
    (
        "remaining_filter",
        PERCENTAGE,
        ReadCommand.filterPercent,
        None,
        None,
        None,
        True,
    ),
    (
        "humidity",
        PERCENTAGE,
        ReadCommand.humidity,
        SensorDeviceClass.HUMIDITY,
        SensorStateClass.MEASUREMENT,
        None,
        True,
    ),
    (
        "exhaust_fan_speed",
        REVOLUTIONS_PER_MINUTE,
        ReadCommand.exhaust_fan_speed,
        None,
        None,
        EntityCategory.DIAGNOSTIC,
        False,
    ),
    (
        "supply_fan_speed",
        REVOLUTIONS_PER_MINUTE,
        ReadCommand.supply_fan_speed,
        None,
        None,
        EntityCategory.DIAGNOSTIC,
        False,
    ),
    (
        "dial_battery",
        PERCENTAGE,
        ReadCommand.battery_percent,
        SensorDeviceClass.BATTERY,
        None,
        EntityCategory.DIAGNOSTIC,
        False,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air sensors."""
    async_add_entities(
        DanfossAirSensor(entry.runtime_data, *sensor)
        for sensor in _SENSORS
    )


class DanfossAirSensor(DanfossAirEntity, SensorEntity):
    """Representation of a Danfoss Air sensor."""

    def __init__(
        self,
        coordinator,
        translation_key,
        unit,
        command,
        device_class,
        state_class,
        entity_category,
        enabled_by_default,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._command = command
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{command.name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category
        self._attr_entity_registry_enabled_default = enabled_by_default

    @property
    def native_value(self):
        """Return the sensor value."""
        return self.coordinator.data.get(self._command)
