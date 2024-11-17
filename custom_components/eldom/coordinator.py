"""The Eldom Coordinator."""

from datetime import timedelta
import logging

from eldom.client import Client as EldomClient

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DEVICE_TYPE_FLAT_BOILER, DEVICE_TYPE_SMART_BOILER, DOMAIN
from .eldom_boiler import FlatEldomBoiler, SmartEldomBoiler

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

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint."""
        devices = await self.api.get_devices()

        flat_boilers: dict[str, FlatEldomBoiler] = {
            device.id: FlatEldomBoiler(
                device.id, await self.api.get_flat_boiler_status(device.id), self.api
            )
            for device in devices
            if device.deviceType == DEVICE_TYPE_FLAT_BOILER
        }

        smart_boilers: dict[str, SmartEldomBoiler] = {
            device.id: SmartEldomBoiler(
                device.id, await self.api.get_smart_boiler_status(device.id), self.api
            )
            for device in devices
            if device.deviceType == DEVICE_TYPE_SMART_BOILER
        }

        return {
            DEVICE_TYPE_FLAT_BOILER: flat_boilers,
            DEVICE_TYPE_SMART_BOILER: smart_boilers,
        }
