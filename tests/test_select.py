"""Tests for Danfoss Air operation mode select entity."""

from homeassistant.helpers import entity_registry as er
from pydanfossair.commands import ReadCommand, UpdateCommand


def _entity_id(hass, entry):
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        "select", "danfoss_air", f"{entry.entry_id}_operation_mode"
    )


async def test_operation_mode_initial_state(hass, setup_integration):
    """Select entity reports the initial operation mode from mock data."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.state == "manual"


async def test_operation_mode_options(hass, setup_integration):
    """Select entity exposes all three options."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)
    state = hass.states.get(entity_id)
    assert set(state.attributes["options"]) == {"demand", "program", "manual"}


async def test_select_demand(hass, setup_integration, mock_danfoss_client):
    """Selecting demand sends operation_mode_demand; refresh returns the new mode from CCM."""
    from .conftest import MOCK_DATA
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    mock_danfoss_client.command.side_effect = lambda cmd: (
        "demand" if cmd == ReadCommand.operation_mode else MOCK_DATA.get(cmd)
    )

    await hass.services.async_call(
        "select", "select_option", {"entity_id": entity_id, "option": "demand"}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.operation_mode_demand)
    assert hass.states.get(entity_id).state == "demand"


async def test_select_program(hass, setup_integration, mock_danfoss_client):
    """Selecting program sends operation_mode_program; refresh returns the new mode from CCM."""
    from .conftest import MOCK_DATA
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    mock_danfoss_client.command.side_effect = lambda cmd: (
        "program" if cmd == ReadCommand.operation_mode else MOCK_DATA.get(cmd)
    )

    await hass.services.async_call(
        "select", "select_option", {"entity_id": entity_id, "option": "program"}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.operation_mode_program)
    assert hass.states.get(entity_id).state == "program"


async def test_select_manual(hass, setup_integration, mock_danfoss_client):
    """Selecting manual sends operation_mode_manual and updates state optimistically."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    await hass.services.async_call(
        "select", "select_option", {"entity_id": entity_id, "option": "manual"}, blocking=True
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.operation_mode_manual)
    assert hass.states.get(entity_id).state == "manual"


async def test_operation_mode_unavailable_on_error(hass, setup_integration, mock_danfoss_client):
    """Select entity goes unavailable when the coordinator fails."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"
