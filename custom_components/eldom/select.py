"""Platform for Eldom select integration."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_E_BOILER_ELDOM, DOMAIN
from .coordinator import EldomCoordinator
from .eldom_boiler import E_BOILER_SMART_CONTROL_MODES, EEldomBoiler
from .models import EldomData


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom select platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    async_add_entities(
        EldomSmartControlModeSelect(e_boiler, eldom_data.coordinator)
        for e_boiler in eldom_data.coordinator.data.get(
            DEVICE_TYPE_E_BOILER_ELDOM, {}
        ).values()
    )


class EldomSmartControlModeSelect(SelectEntity, CoordinatorEntity):
    """Representation of an electric boiler's "Smart control" mode."""

    def __init__(
        self, eldom_boiler: EEldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize the "Smart control" mode select."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this select."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._eldom_boiler.device_id)},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-smart-control-mode-select"

    @property
    def name(self) -> str:
        """Return the name of the select."""
        return f"{self._eldom_boiler.name}'s Smart Control Mode"

    @property
    def icon(self) -> str:
        """Return the icon of the select."""
        return "mdi:leaf"

    @property
    def options(self) -> list[str]:
        """Return the available modes."""
        return list(E_BOILER_SMART_CONTROL_MODES.values())

    @property
    def current_option(self) -> str:
        """Return the current mode."""
        return self._eldom_boiler.smart_control_mode

    async def async_select_option(self, option: str) -> None:
        """Change the mode."""
        await self._eldom_boiler.set_smart_control_mode(option)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._eldom_boiler = self.coordinator.data.get(self._eldom_boiler.type).get(
            self._eldom_boiler.id
        )

        self.async_write_ha_state()
