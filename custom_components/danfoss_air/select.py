"""Support for Danfoss Air HRV operation mode select."""

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

PARALLEL_UPDATES = 1

_OPERATION_MODE_COMMANDS = {
    "demand": UpdateCommand.operation_mode_demand,
    "program": UpdateCommand.operation_mode_program,
    "manual": UpdateCommand.operation_mode_manual,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air select entities."""
    async_add_entities([DanfossAirOperationMode(entry.runtime_data)])


class DanfossAirOperationMode(DanfossAirEntity, SelectEntity):
    """Select entity for the CCM operation mode."""

    _attr_translation_key = "operation_mode"
    _attr_options = list(_OPERATION_MODE_COMMANDS)

    def __init__(self, coordinator) -> None:
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_operation_mode"

    @property
    def current_option(self) -> str | None:
        """Return the current operation mode."""
        return self.coordinator.data.get(ReadCommand.operation_mode)

    async def async_select_option(self, option: str) -> None:
        """Change the operation mode and refresh so fan_step reflects the actual CCM state."""
        await self.coordinator.async_send_command(_OPERATION_MODE_COMMANDS[option])
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, ReadCommand.operation_mode: option}
        )
        await self.coordinator.async_request_refresh()
