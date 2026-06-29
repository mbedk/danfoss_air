"""Tests for Danfoss Air fan step number entity."""

import pytest
from homeassistant.helpers import entity_registry as er
from pydanfossair.commands import ReadCommand, UpdateCommand


def _entity_id(hass, entry):
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        "number", "danfoss_air", f"{entry.entry_id}_fan_step"
    )


async def test_fan_step_initial_state(hass, setup_integration):
    """Fan step reports the correct initial value (60% → step 6)."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert float(state.state) == pytest.approx(6.0)


async def test_fan_step_set_value(hass, setup_integration, mock_danfoss_client):
    """Setting fan step sends the correct UpdateCommand and updates state optimistically."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": entity_id, "value": 8},
        blocking=True,
    )
    await hass.async_block_till_done()

    mock_danfoss_client.command.assert_any_call(UpdateCommand.set_fan_step_8)
    assert float(hass.states.get(entity_id).state) == pytest.approx(8.0)


async def test_fan_step_all_steps(hass, setup_integration, mock_danfoss_client):
    """Each step 1–10 sends the correct UpdateCommand."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    expected_commands = {
        1: UpdateCommand.set_fan_step_1,
        2: UpdateCommand.set_fan_step_2,
        3: UpdateCommand.set_fan_step_3,
        4: UpdateCommand.set_fan_step_4,
        5: UpdateCommand.set_fan_step_5,
        6: UpdateCommand.set_fan_step_6,
        7: UpdateCommand.set_fan_step_7,
        8: UpdateCommand.set_fan_step_8,
        9: UpdateCommand.set_fan_step_9,
        10: UpdateCommand.set_fan_step_10,
    }

    for step, expected_cmd in expected_commands.items():
        mock_danfoss_client.command.reset_mock()
        await hass.services.async_call(
            "number",
            "set_value",
            {"entity_id": entity_id, "value": step},
            blocking=True,
        )
        await hass.async_block_till_done()
        mock_danfoss_client.command.assert_any_call(expected_cmd)
        assert float(hass.states.get(entity_id).state) == pytest.approx(float(step))


async def test_fan_step_unavailable_on_error(hass, setup_integration, mock_danfoss_client):
    """Fan step goes unavailable when the coordinator fails."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"


async def test_fan_step_switches_to_manual_when_in_demand_mode(hass, setup_integration, mock_danfoss_client):
    """Moving the slider in demand mode sends manual command first, then the step command."""
    from .conftest import MOCK_DATA
    entry = setup_integration
    entity_id = _entity_id(hass, entry)

    mock_danfoss_client.command.side_effect = lambda cmd: (
        "demand" if cmd == ReadCommand.operation_mode else MOCK_DATA.get(cmd)
    )
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    mock_danfoss_client.command.reset_mock()
    await hass.services.async_call(
        "number", "set_value", {"entity_id": entity_id, "value": 5}, blocking=True
    )
    await hass.async_block_till_done()

    calls = [c.args[0] for c in mock_danfoss_client.command.call_args_list]
    assert UpdateCommand.operation_mode_manual in calls
    assert UpdateCommand.set_fan_step_5 in calls
    assert calls.index(UpdateCommand.operation_mode_manual) < calls.index(UpdateCommand.set_fan_step_5)
    assert float(hass.states.get(entity_id).state) == pytest.approx(5.0)
