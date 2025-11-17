"""Config flow for Eldom integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import aiohttp_client

from .const import API_CHOICES, CONF_API, DOMAIN, ELDOM_API
from .eldom_client import EldomClientWrapper

_LOGGER = logging.getLogger(__name__)


class EldomConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Eldom."""

    VERSION = 1

    async def _async_validate_credentials(
        self, username: str, password: str, api: str
    ) -> str | None:
        """Validate the credentials. Return an error string, or None if successful."""
        session = aiohttp_client.async_create_clientsession(self.hass)

        client = EldomClientWrapper(session, username, password, api)

        await client.login()
        connected = await client.is_connected()
        if connected is False:
            _LOGGER.error(
                "Config flow failed to login to Eldom API '%s' with '%s'", api, username
            )
            return "Authentication failed. Please check your credentials."

        _LOGGER.info(
            "Successfully authenticated config flow with Eldom API '%s' with '%s'",
            api,
            username,
        )
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            unique_id = f"{user_input[CONF_USERNAME].lower()}-{user_input[CONF_API]}"
            _LOGGER.debug("Registering user with unique ID: '%s'", unique_id)
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            _LOGGER.debug(
                "Successfully configured user with unique ID: '%s'", unique_id
            )

            error = await self._async_validate_credentials(
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_API],
            )
            if error is None:
                return self.async_create_entry(
                    title=user_input[CONF_USERNAME], data=user_input
                )

            errors["base"] = error

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(CONF_API, default=ELDOM_API): vol.In(API_CHOICES),
                }
            ),
            errors=errors,
        )
