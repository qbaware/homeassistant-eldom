"""The Eldom Coordinator."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .eldom_client import EldomClientWrapper

_LOGGER = logging.getLogger(__name__)


class EldomCoordinator(DataUpdateCoordinator):
    """Eldom coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        eldom_wrapper_client: EldomClientWrapper,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.eldom_wrapper_client = eldom_wrapper_client

    async def _async_update_data(self) -> dict:
        """Fetch data from Eldom."""

        return await self.eldom_wrapper_client.get_devices()
