"""The Eldom integration."""

from __future__ import annotations

import logging

from eldom.client import Client as EldomClient

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import aiohttp_client

from .const import API_BASE_URL, DOMAIN
from .coordinator import EldomCoordinator
from .models import EldomData

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eldom from a config entry."""

    base_url = API_BASE_URL
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]

    session = aiohttp_client.async_create_clientsession(hass)
    api_client = EldomClient(base_url, session)

    try:
        await api_client.login(email, password)
        await api_client.get_devices()  # NOTE: This is needed since currently the login API does not throw an error if the credentials are invalid: https://github.com/qbaware/homeassistant-eldom/issues/27
        _LOGGER.info("Successfully authenticated with Eldom API with '%s'", email)
    except Exception as e:
        _LOGGER.error(
            "Unexpected exception while authenticating with Eldom API for '%s': %s",
            email,
            e,
        )
        raise ConfigEntryNotReady(
            f"Unexpected exception while authenticating with Eldom API for '{email}': {e}"
        ) from e

    coordinator = EldomCoordinator(hass, api_client)

    eldom_data = EldomData(api_client, coordinator)

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = eldom_data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    hass.data[DOMAIN].pop(entry.entry_id)

    return True
