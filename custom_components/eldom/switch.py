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

REQUIRED_OPERATION_MODE_FOR_BOOST = 2
SWITCH_NAME = "Powerful"

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
        self._id = f"{self._flat_boiler_id}-powerful-switch"

        self._powerful_enabled = self.coordinator.data[self._flat_boiler_id].HasBoost
        self._eco_mode_selected = (
            self.coordinator.data[self._flat_boiler_id].State
            == REQUIRED_OPERATION_MODE_FOR_BOOST
        )

    @property
    def name(self) -> str:
        """Return the name of the powerful mode switch."""
        return SWITCH_NAME

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
        return self._id

    @property
    def is_on(self) -> bool:
        """Return the powerful status."""
        return self._powerful_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn powerful on."""
        if not self._eco_mode_selected:
            _LOGGER.warning("Powerful mode can only be turned on when in ECO mode")
            return

        self._powerful_enabled = True
        self.schedule_update_ha_state()

        await self._api.set_flat_boiler_powerful_mode_on(self._flat_boiler_id)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn powerful off."""
        _LOGGER.warning(
            "Powerful mode cannot be turned off, change the mode to something else to disable the powerful mode"
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._powerful_enabled = self.coordinator.data[self._flat_boiler_id].HasBoost
        self._eco_mode_selected = (
            self.coordinator.data[self._flat_boiler_id].State
            == REQUIRED_OPERATION_MODE_FOR_BOOST
        )

        self.async_write_ha_state()
