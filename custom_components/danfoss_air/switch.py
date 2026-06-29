"""Support for Danfoss Air HRV switches."""

import logging
from typing import Any

from pydanfossair.commands import ReadCommand, UpdateCommand

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DanfossAirConfigEntry
from .entity import DanfossAirEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1

_SWITCHES = [
    (
        "boost",
        ReadCommand.boost,
        UpdateCommand.boost_activate,
        UpdateCommand.boost_deactivate,
    ),
    (
        "bypass",
        ReadCommand.bypass,
        UpdateCommand.bypass_activate,
        UpdateCommand.bypass_deactivate,
    ),
    (
        "automatic_bypass",
        ReadCommand.automatic_bypass,
        UpdateCommand.automatic_bypass_activate,
        UpdateCommand.automatic_bypass_deactivate,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Danfoss Air switches."""
    async_add_entities(
        DanfossAirSwitch(entry.runtime_data, translation_key, state_cmd, on_cmd, off_cmd)
        for translation_key, state_cmd, on_cmd, off_cmd in _SWITCHES
    )


class DanfossAirSwitch(DanfossAirEntity, SwitchEntity):
    """Representation of a Danfoss Air switch."""

    def __init__(
        self,
        coordinator,
        translation_key: str,
        state_command: ReadCommand,
        on_command: UpdateCommand,
        off_command: UpdateCommand,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._state_command = state_command
        self._on_command = on_command
        self._off_command = off_command
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{state_command.name}"

    @property
    def is_on(self) -> bool | None:
        """Return the switch state."""
        return self.coordinator.data.get(self._state_command)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self._async_set(self._on_command, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self._async_set(self._off_command, False)

    async def _async_set(self, command: UpdateCommand, state: bool) -> None:
        """Send a command and optimistically apply the intended state.

        We use the intended boolean rather than the value returned by the
        command: pydanfossair's write path reports the raw register bit, but
        automatic_bypass stores an inverted bit, so trusting the return value
        would show the switch in the wrong state until the next poll.
        """
        _LOGGER.debug("Setting %s to %s", self._attr_translation_key, state)
        await self.coordinator.async_send_command(command)
        self.coordinator.async_set_updated_data(
            {**self.coordinator.data, self._state_command: state}
        )
