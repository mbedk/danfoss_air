"""Diagnostics support for Danfoss Air."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import DanfossAirConfigEntry


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: DanfossAirConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data
    return {
        "host": coordinator.host,
        "data": {str(k): v for k, v in coordinator.data.items()},
    }
