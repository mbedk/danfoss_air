"""Support for the for Danfoss Air HRV binary sensors."""

from pydanfossair.commands import ReadCommand

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_SENSORS = [
    ("Bypass Active", ReadCommand.bypass, BinarySensorDeviceClass.OPENING),
    ("Away Mode Active", ReadCommand.away_mode, None),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air binary sensors from a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        DanfossAirBinarySensor(data, name, command, device_class)
        for name, command, device_class in _SENSORS
    )


class DanfossAirBinarySensor(BinarySensorEntity):
    """Representation of a Danfoss Air binary sensor."""

    _attr_has_entity_name = True

    def __init__(self, data, name, sensor_type, device_class):
        """Initialize the binary sensor."""
        self._data = data
        self._type = sensor_type
        self._attr_name = name
        self._attr_unique_id = f"{data.host}_{sensor_type.name}"
        self._attr_device_class = device_class
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, data.host)},
            name="Danfoss Air",
            manufacturer="Danfoss",
            model="Air CCM",
        )

    def update(self) -> None:
        """Fetch new state data for the sensor."""
        self._data.update()
        self._attr_is_on = self._data.get_value(self._type)
