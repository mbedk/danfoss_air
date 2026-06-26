"""Support for the for Danfoss Air HRV sensors."""

import logging

from pydanfossair.commands import ReadCommand

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

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
    ("Fan Step", PERCENTAGE, ReadCommand.fan_step, None, None),
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
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DanfossAirSensor(data, name, unit, command, device_class, state_class)
        for name, unit, command, device_class, state_class in _SENSORS
    )


class DanfossAirSensor(SensorEntity):
    """Representation of a Danfoss Air sensor."""

    _attr_has_entity_name = True

    def __init__(self, data, name, sensor_unit, sensor_type, device_class, state_class):
        """Initialize the sensor."""
        self._data = data
        self._type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{data.host}_{sensor_type.name}"
        self._attr_native_unit_of_measurement = sensor_unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.host)},
            name="Danfoss Air",
            manufacturer="Danfoss",
            model="Air CCM",
        )

    def update(self) -> None:
        """Update the sensor state."""
        self._data.update()
        self._attr_native_value = self._data.get_value(self._type)
        if self._attr_native_value is None:
            _LOGGER.debug("Could not get data for %s", self._type)
