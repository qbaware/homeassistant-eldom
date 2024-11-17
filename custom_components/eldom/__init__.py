"""The Eldom integration."""

from __future__ import annotations

import logging

from eldom.client import Client as EldomClient
import requests

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client

from .const import API_BASE_URL, DOMAIN
from .coordinator import EldomCoordinator
from .models import EldomData

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.WATER_HEATER,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Eldom from a config entry."""

    base_url = API_BASE_URL
    email = entry.data[CONF_EMAIL]
    password = entry.data[CONF_PASSWORD]

    session = aiohttp_client.async_get_clientsession(hass)
    api_client = EldomClient(base_url, session)

    try:
        await api_client.login(email, password)
        _LOGGER.info("Successfully logged in to Eldom API")
    except requests.exceptions.HTTPError as e:
        _LOGGER.error("Failed to login to Eldom API: %s", e)
        return False

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
