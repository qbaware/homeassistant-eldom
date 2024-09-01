"""Config flow for Eldom integration."""

from __future__ import annotations

import logging
from typing import Any

from eldom.flat_boiler import Client as EldomClient
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.helpers import aiohttp_client
import homeassistant.helpers.config_validation as cv

from .const import API_BASE_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


class EldomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eldom."""

    VERSION = 1

    async def _async_validate_credentials(
        self, email: str, password: str
    ) -> str | None:
        """Validate the credentials. Return an error string, or None if successful."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        client: EldomClient = EldomClient(API_BASE_URL, session)

        try:
            await client.login(email, password)
        except Exception as e:
            _LOGGER.exception("Failed to login to Eldom API")
            return e

        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            unique_id = user_input[CONF_EMAIL].lower()
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()

            error = await self._async_validate_credentials(
                user_input[CONF_EMAIL], user_input[CONF_PASSWORD]
            )
            if error is None:
                return self.async_create_entry(
                    title=user_input[CONF_EMAIL], data=user_input
                )

            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
