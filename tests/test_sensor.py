"""Tests for Danfoss Air sensors."""

import pytest
from homeassistant.helpers import entity_registry as er
from pydanfossair.commands import ReadCommand

from .conftest import MOCK_HOST


def _entity_id(hass, entry, platform, command_name):
    """Look up an entity ID by unique_id via the entity registry."""
    ent_reg = er.async_get(hass)
    return ent_reg.async_get_entity_id(
        platform, "danfoss_air", f"{entry.entry_id}_{command_name}"
    )


async def test_temperature_sensors(hass, setup_integration):
    """Temperature sensors report values from the coordinator."""
    entry = setup_integration

    cases = {
        "exhaustTemperature": 22.5,
        "outdoorTemperature": 5.0,
        "supplyTemperature": 18.0,
        "extractTemperature": 21.0,
    }
    for command_name, expected in cases.items():
        entity_id = _entity_id(hass, entry, "sensor", command_name)
        assert entity_id is not None, f"Entity for {command_name} not found"
        state = hass.states.get(entity_id)
        assert state is not None
        assert float(state.state) == pytest.approx(expected)


async def test_humidity_and_filter_sensors(hass, setup_integration):
    """Humidity and filter sensors report rounded values."""
    entry = setup_integration

    for command_name, expected in [("humidity", 48.5), ("filterPercent", 75.0)]:
        entity_id = _entity_id(hass, entry, "sensor", command_name)
        assert entity_id is not None
        state = hass.states.get(entity_id)
        assert float(state.state) == pytest.approx(expected)


async def test_diagnostic_sensors_disabled_by_default(hass, setup_integration):
    """Fan speed and battery sensors are disabled by default."""
    entry = setup_integration
    ent_reg = er.async_get(hass)

    for command_name in ("exhaust_fan_speed", "supply_fan_speed", "battery_percent"):
        entity_id = _entity_id(hass, entry, "sensor", command_name)
        assert entity_id is not None, f"Entity for {command_name} not in registry"
        entity_entry = ent_reg.async_get(entity_id)
        assert entity_entry.disabled_by is not None, (
            f"{command_name} should be disabled by default"
        )


async def test_sensors_become_unavailable_on_error(hass, setup_integration, mock_danfoss_client):
    """Sensors go unavailable when the coordinator cannot reach the CCM."""
    entry = setup_integration

    entity_id = _entity_id(hass, entry, "sensor", "exhaustTemperature")
    assert hass.states.get(entity_id).state == "22.5"

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(entity_id).state == "unavailable"


async def test_fan_step_sensor(hass, setup_integration):
    """Fan step sensor shows the current step (1–10) from the coordinator."""
    entry = setup_integration
    ent_reg = er.async_get(hass)
    entity_id = ent_reg.async_get_entity_id("sensor", "danfoss_air", f"{entry.entry_id}_fan_step")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert int(state.state) == 6  # MOCK_DATA fan_step=60 → 60//10 = 6


async def test_fan_step_sensor_updates_in_demand_mode(hass, setup_integration, mock_danfoss_client):
    """Fan step sensor reflects the CCM's actual step even in demand mode."""
    from .conftest import MOCK_DATA
    entry = setup_integration
    ent_reg = er.async_get(hass)
    entity_id = ent_reg.async_get_entity_id("sensor", "danfoss_air", f"{entry.entry_id}_fan_step")

    mock_danfoss_client.command.side_effect = lambda cmd: (
        "demand" if cmd == ReadCommand.operation_mode
        else 30 if cmd == ReadCommand.fan_step  # step 3
        else MOCK_DATA.get(cmd)
    )
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()

    assert int(hass.states.get(entity_id).state) == 3


async def test_sensors_recover_after_error(hass, setup_integration, mock_danfoss_client):
    """Sensors recover once the coordinator can reach the CCM again."""
    entry = setup_integration
    entity_id = _entity_id(hass, entry, "sensor", "exhaustTemperature")

    mock_danfoss_client.command.side_effect = Exception("Lost connection")
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "unavailable"

    from .conftest import _command_side_effect
    mock_danfoss_client.command.side_effect = _command_side_effect
    await entry.runtime_data.async_refresh()
    await hass.async_block_till_done()
    assert float(hass.states.get(entity_id).state) == pytest.approx(22.5)
