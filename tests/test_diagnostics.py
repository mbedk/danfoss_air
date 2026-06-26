"""Tests for Danfoss Air diagnostics."""

from custom_components.danfoss_air.diagnostics import async_get_config_entry_diagnostics

from .conftest import MOCK_HOST


async def test_diagnostics_returns_host(hass, setup_integration):
    """Diagnostics includes the configured host."""
    entry = setup_integration
    result = await async_get_config_entry_diagnostics(hass, entry)
    assert result["host"] == MOCK_HOST


async def test_diagnostics_returns_data(hass, setup_integration):
    """Diagnostics includes a non-empty data dict with stringified keys."""
    entry = setup_integration
    result = await async_get_config_entry_diagnostics(hass, entry)
    assert "data" in result
    assert len(result["data"]) > 0
    # Keys are stringified ReadCommand enum members
    assert all(isinstance(k, str) for k in result["data"])
