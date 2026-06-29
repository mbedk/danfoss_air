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
        SensorStateClass.MEASUREMENT,
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
    entities: list[SensorEntity] = [
        DanfossAirSensor(entry.runtime_data, *sensor) for sensor in _SENSORS
    ]
    entities.append(DanfossAirFanStepSensor(entry.runtime_data))
    async_add_entities(entities)


class DanfossAirFanStepSensor(DanfossAirEntity, SensorEntity):
    """Read-only sensor showing the current fan step (1–10) as reported by the CCM."""

    _attr_translation_key = "fan_step"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_fan_step"

    @property
    def native_value(self) -> int | None:
        raw = self.coordinator.data.get(ReadCommand.fan_step)
        if raw is None:
            return None
        return raw // 10


class DanfossAirSensor(DanfossAirEntity, SensorEntity):
    """Representation of a Danfoss Air sensor."""

    def __init__(
        self,
        coordinator,
        translation_key: str,
        unit: str | None,
        command: ReadCommand,
        device_class: SensorDeviceClass | None,
        state_class: SensorStateClass | None,
        entity_category: EntityCategory | None,
        enabled_by_default: bool,
    ) -> None:
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
    def native_value(self) -> float | None:
        """Return the sensor value."""
        return self.coordinator.data.get(self._command)
