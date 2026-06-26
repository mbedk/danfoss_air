"""Tests for Danfoss Air binary sensors."""

from homeassistant.helpers import entity_registry as er

from pydanfossair.commands import ReadCommand

from .conftest import MOCK_DATA


def _entity_id(hass, entry, command_name):
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        "binary_sensor", "danfoss_air", f"{entry.entry_id}_{command_name}"
    )


async def test_binary_sensor_initial_states(hass, setup_integration):
    """Binary sensors report the correct initial states."""
    entry = setup_integration

    for command_name, expected in [("bypass", "off"), ("away_mode", "off")]:
        entity_id = _entity_id(hass, entry, command_name)
        assert entity_id is not None, f"Entity for {command_name} not found"
        state = hass.states.get(entity_id)
        assert state is not None
        assert state.state == expected


async def test_binary_sensor_on_state(hass, setup_integration, mock_danfoss_client):
    """Binary sensors reflect True values from the coordinator."""
    entry = setup_integration

    from .conftest import MOCK_DATA, _command_side_effect

    updated_data = {**MOCK_DATA, ReadCommand.bypass: True}
    mock_danfoss_client.command.side_effect = lambda cmd: updated_data.get(cmd) if cmd in updated_data else _command_side_effect(cmd)
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    entity_id = _entity_id(hass, entry, "bypass")
    assert hass.states.get(entity_id).state == "on"


async def test_binary_sensors_unavailable_on_error(hass, setup_integration, mock_danfoss_client):
    """Binary sensors go unavailable when the coordinator fails."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "bypass")

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"
