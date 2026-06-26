"""Tests for Danfoss Air integration setup and unload."""

from unittest.mock import patch

from homeassistant.config_entries import ConfigEntryState


async def test_setup_entry(hass, setup_integration):
    """Integration loads successfully."""
    entry = setup_integration
    assert entry.state == ConfigEntryState.LOADED


async def test_unload_entry(hass, setup_integration):
    """Integration unloads cleanly."""
    entry = setup_integration
    await hass.config_entries.async_unload(entry.entry_id)
    assert entry.state == ConfigEntryState.NOT_LOADED


async def test_setup_entry_connection_error(hass, mock_config_entry):
    """ConfigEntryNotReady is triggered when the CCM is unreachable at startup."""
    with patch(
        "custom_components.danfoss_air.coordinator.DanfossClient"
    ) as mock:
        mock.return_value.command.side_effect = Exception("Connection refused")
        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()
        assert mock_config_entry.state == ConfigEntryState.SETUP_RETRY
