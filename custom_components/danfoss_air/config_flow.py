"""Config flow for Danfoss Air."""

import logging

from pydanfossair.commands import ReadCommand
from pydanfossair.danfossclient import DanfossClient
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class DanfossAirConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Danfoss Air."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                await self.hass.async_add_executor_job(self._test_connection, host)
            except Exception:
                _LOGGER.exception("Failed to connect to Danfoss Air CCM at %s", host)
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title="Danfoss Air", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    @staticmethod
    def _test_connection(host: str) -> None:
        """Test that the CCM unit is reachable by reading one value."""
        client = DanfossClient(host)
        client.command(ReadCommand.exhaustTemperature)
