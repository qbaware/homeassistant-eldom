"""Switch platform for Eldom integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER_NAME
from .models import EldomData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom switch platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EldomPowerfulModeSwitch(flat_boiler.DeviceID, eldom_data)
        for _, flat_boiler in enumerate(eldom_data.coordinator.data.values())
    )


class EldomPowerfulModeSwitch(SwitchEntity, CoordinatorEntity):
    """Representation of Eldom powerful switch."""

    def __init__(self, flat_boiler_id: str, eldom_data: EldomData) -> None:
        """Initialize an Eldom powerful control."""
        super().__init__(eldom_data.coordinator)
        self._flat_boiler_id = flat_boiler_id
        self._api = eldom_data.api
        self._name = f"{self._flat_boiler_id}-powerful"

        self._powerful_enabled = self.coordinator.data[self._flat_boiler_id].HasBoost
        self._eco_mode_selected = (
            self.coordinator.data[self._flat_boiler_id].State == 2
        )  # TODO: Read this from constants.

    @property
    def name(self) -> str:
        """Return the name of the powerful mode switch."""
        return "Powerful"

    @property
    def icon(self) -> str:
        """Return the icon of the powerful mode switch."""
        return "mdi:rocket-launch"

    @property
    def device_class(self) -> SwitchDeviceClass:
        """Return the device class of the powerful mode switch."""
        return SwitchDeviceClass.SWITCH

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._flat_boiler_id)},
            manufacturer=MANUFACTURER_NAME,
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return self._name

    @property
    def is_on(self) -> bool:
        """Return the powerful status."""
        return self._powerful_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn powerful on."""
        _LOGGER.error("Powerful mode is not supported yet")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn powerful off."""
        _LOGGER.error("Powerful mode is not supported yet")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._powerful_enabled = self.coordinator.data[self._flat_boiler_id].HasBoost
        self._eco_mode_selected = (
            self.coordinator.data[self._flat_boiler_id].State == 2
        )  # TODO: Read this from constants.

        self.async_write_ha_state()
