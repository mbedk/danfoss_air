"""Tests for Danfoss Air switches."""

from homeassistant.helpers import entity_registry as er
from pydanfossair.commands import UpdateCommand


def _entity_id(hass, entry, command_name):
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        "switch", "danfoss_air", f"{entry.entry_id}_{command_name}"
    )


async def test_switch_initial_states(hass, setup_integration):
    """All switches start off."""
    entry = setup_integration

    for command_name in ("boost", "bypass", "automatic_bypass"):
        entity_id = _entity_id(hass, entry, command_name)
        assert entity_id is not None, f"Entity for {command_name} not found"
        assert hass.states.get(entity_id).state == "off"


async def test_boost_turn_on(hass, setup_integration, mock_danfoss_client):
    """Turning on boost sends boost_activate and updates state optimistically."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "boost")

    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.boost_activate)
    assert hass.states.get(entity_id).state == "on"


async def test_boost_turn_off(hass, setup_integration, mock_danfoss_client):
    """Turning off boost sends boost_deactivate and updates state optimistically."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "boost")

    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.boost_deactivate)
    assert hass.states.get(entity_id).state == "off"


async def test_bypass_turn_on(hass, setup_integration, mock_danfoss_client):
    """Turning on bypass sends bypass_activate."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "bypass")

    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.bypass_activate)
    assert hass.states.get(entity_id).state == "on"


async def test_switches_unavailable_on_error(hass, setup_integration, mock_danfoss_client):
    """Switches go unavailable when the coordinator fails."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "boost")

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"
