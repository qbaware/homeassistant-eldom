"""Switch platform for Eldom integration."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_FLAT_BOILER, DEVICE_TYPE_SMART_BOILER, DOMAIN
from .coordinator import EldomCoordinator
from .eldom_boiler import OPERATION_MODES, EldomBoiler
from .models import EldomData

REQUIRED_OPERATION_MODE_FOR_BOOST = OPERATION_MODES[2]
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
        EldomBoilerPowerfulModeSwitch(flat_boiler, eldom_data.coordinator)
        for flat_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_FLAT_BOILER, []
        ).values()
    )

    async_add_entities(
        EldomBoilerPowerfulModeSwitch(smart_boiler, eldom_data.coordinator)
        for smart_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_SMART_BOILER, []
        ).values()
    )


class EldomBoilerPowerfulModeSwitch(SwitchEntity, CoordinatorEntity):
    """Representation of Eldom powerful switch."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom powerful control."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-powerful-switch"

    @property
    def name(self) -> str:
        """Return the name of the powerful mode switch."""
        return f"{self._eldom_boiler.name}'s {SWITCH_NAME} Switch"

    @property
    def icon(self) -> str:
        """Return the icon of the powerful mode switch."""
        return "mdi:rocket-launch"

    @property
    def device_class(self) -> SwitchDeviceClass:
        """Return the device class of the powerful mode switch."""
        return SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool:
        """Return the powerful status."""
        return self._eldom_boiler.powerful_enabled

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn powerful on."""
        eco_mode_enabled = (
            self._eldom_boiler.current_operation == REQUIRED_OPERATION_MODE_FOR_BOOST
        )
        if not eco_mode_enabled:
            _LOGGER.warning("Powerful mode can only be turned on when in ECO mode")
            return

        await self._eldom_boiler.enable_powerful_mode()
        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn powerful off."""
        _LOGGER.warning(
            "Powerful mode cannot be turned off, change the mode to something else to disable the powerful mode"
        )

        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()
