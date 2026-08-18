"""The Eldom integration."""

from __future__ import annotations

import logging

from eldom.client import InvalidCredentialsError as EldomInvalidCredentialsError
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client
from ioteldom.client import InvalidCredentialsError as IoTEldomInvalidCredentialsError

from .const import CONF_API, DOMAIN
from .coordinator import EldomCoordinator
from .eldom_client import EldomClientWrapper
from .models import EldomData

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eldom from a config entry."""
    session = aiohttp_client.async_create_clientsession(hass)

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    api = entry.data[CONF_API]

    client = EldomClientWrapper(session, username, password, api)

    await client.login()

    try:
        connected = await client.is_connected()
    except (EldomInvalidCredentialsError, IoTEldomInvalidCredentialsError) as err:
        _LOGGER.error(
            "Invalid credentials for Eldom API '%s' for '%s'", api, username
        )
        raise ConfigEntryAuthFailed(
            f"Invalid credentials for Eldom API '{api}' for '{username}'"
        ) from err

    if connected is False:
        _LOGGER.error(
            "Unexpected exception while authenticating with Eldom API '%s' for '%s'",
            api,
            username,
        )
        raise ConfigEntryNotReady(
            f"Unexpected exception while authenticating with Eldom API '{api}' for '{username}'"
        )

    coordinator = EldomCoordinator(hass, client)

    eldom_data = EldomData(coordinator)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = eldom_data

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.info("Initial data fetch failed, deferring setup: %s", err)
        raise ConfigEntryNotReady from err

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data[DOMAIN].pop(entry.entry_id)

    return True
