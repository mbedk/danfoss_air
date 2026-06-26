"""Shared fixtures for Danfoss Air tests."""

from unittest.mock import MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.const import CONF_HOST
from pydanfossair.commands import ReadCommand

MOCK_HOST = "192.168.1.100"

MOCK_DATA = {
    ReadCommand.exhaustTemperature: 22.5,
    ReadCommand.outdoorTemperature: 5.0,
    ReadCommand.supplyTemperature: 18.0,
    ReadCommand.extractTemperature: 21.0,
    ReadCommand.humidity: 48.5,
    ReadCommand.filterPercent: 75.0,
    ReadCommand.bypass: False,
    ReadCommand.fan_step: 60,  # 60% = step 6
    ReadCommand.supply_fan_speed: 1800,
    ReadCommand.exhaust_fan_speed: 1900,
    ReadCommand.away_mode: False,
    ReadCommand.boost: False,
    ReadCommand.battery_percent: 85.0,
    ReadCommand.automatic_bypass: False,
}


def _command_side_effect(cmd):
    """Return MOCK_DATA for ReadCommands; derive bool from last byte for UpdateCommands."""
    if cmd in MOCK_DATA:
        return MOCK_DATA[cmd]
    if isinstance(cmd.value, (bytes, bytearray)):
        return bool(cmd.value[-1])
    return None


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for all tests."""
    yield


@pytest.fixture
def mock_danfoss_client():
    """Patch DanfossClient so no real network calls are made."""
    with patch(
        "custom_components.danfoss_air.coordinator.DanfossClient"
    ) as mock_class:
        client = MagicMock()
        client.command.side_effect = _command_side_effect
        mock_class.return_value = client
        yield client


@pytest.fixture
def mock_config_entry():
    """Return a MockConfigEntry for Danfoss Air."""
    return MockConfigEntry(
        domain="danfoss_air",
        title="Danfoss Air",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_HOST,
    )


@pytest.fixture
async def setup_integration(hass, mock_config_entry, mock_danfoss_client):
    """Set up the integration and return the config entry."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
