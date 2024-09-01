"""The Eldom Coordinator."""

from datetime import timedelta
import logging

from eldom.flat_boiler import Client as EldomClient
from eldom.models import FlatBoilerDetails

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEVICE_TYPE_FLAT_BOILER, DOMAIN

_LOGGER = logging.getLogger(__name__)


class EldomCoordinator(DataUpdateCoordinator):
    """Eldom coordinator."""

    def __init__(self, hass: HomeAssistant, api: EldomClient) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.api = api

    async def _async_update_data(self) -> list[FlatBoilerDetails]:
        """Fetch data from API endpoint."""
        flat_boilers: list[FlatBoilerDetails] = [
            await self.api.get_flat_boiler_status(device.id)
            for device in await self.api.get_devices()
            if device.deviceType == DEVICE_TYPE_FLAT_BOILER
        ]

        return {flat_boiler.DeviceID: flat_boiler for flat_boiler in flat_boilers}
