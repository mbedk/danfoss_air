"""Tests for the Danfoss Air config flow."""

from unittest.mock import patch

import pytest
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResultType

from pytest_homeassistant_custom_component.common import MockConfigEntry

from .conftest import MOCK_HOST


@pytest.fixture
def mock_connection_ok():
    """Patch config_flow.DanfossClient to succeed."""
    with patch("custom_components.danfoss_air.config_flow.DanfossClient") as mock:
        mock.return_value.command.return_value = 22.5
        yield mock


@pytest.fixture
def mock_connection_fail():
    """Patch config_flow.DanfossClient to raise on connect."""
    with patch("custom_components.danfoss_air.config_flow.DanfossClient") as mock:
        mock.return_value.command.side_effect = Exception("Connection refused")
        yield mock


async def test_user_flow_shows_form(hass, mock_connection_ok):
    """The initial step shows the host form."""
    result = await hass.config_entries.flow.async_init(
        "danfoss_air", context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"
    assert not result["errors"]


async def test_user_flow_success(hass, mock_connection_ok):
    """A valid host creates a config entry."""
    result = await hass.config_entries.flow.async_init(
        "danfoss_air", context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Danfoss Air"
    assert result["data"] == {CONF_HOST: MOCK_HOST}


async def test_user_flow_cannot_connect(hass, mock_connection_fail):
    """A connection error shows the cannot_connect error and re-shows the form."""
    result = await hass.config_entries.flow.async_init(
        "danfoss_air", context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}


async def test_user_flow_already_configured(hass, mock_connection_ok):
    """A duplicate host aborts with already_configured."""
    entry = MockConfigEntry(
        domain="danfoss_air",
        data={CONF_HOST: MOCK_HOST},
        unique_id=MOCK_HOST,
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        "danfoss_air", context={"source": config_entries.SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: MOCK_HOST}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_shows_form(hass, setup_integration, mock_connection_ok):
    """The reconfigure step shows the host form pre-filled with current host."""
    entry = setup_integration
    result = await hass.config_entries.flow.async_init(
        "danfoss_air",
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "reconfigure"


async def test_reconfigure_success(hass, setup_integration, mock_connection_ok):
    """A valid new host updates the config entry and reloads."""
    entry = setup_integration
    new_host = "192.168.1.200"

    result = await hass.config_entries.flow.async_init(
        "danfoss_air",
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: new_host}
    )
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert entry.data[CONF_HOST] == new_host


async def test_reconfigure_cannot_connect(hass, setup_integration, mock_connection_fail):
    """A connection error during reconfigure re-shows the form with an error."""
    entry = setup_integration
    result = await hass.config_entries.flow.async_init(
        "danfoss_air",
        context={"source": config_entries.SOURCE_RECONFIGURE, "entry_id": entry.entry_id},
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.200"}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}
