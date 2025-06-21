"""Button to reset energy usage for Eldom boiler devices."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEVICE_TYPE_FLAT_BOILER, DEVICE_TYPE_SMART_BOILER, DOMAIN
from .coordinator import EldomCoordinator
from .eldom_boiler import EldomBoiler
from .models import EldomData

RESET_ENERGY_USAGE_BUTTON = "Reset Energy Usage Button"
RESET_ENERGY_USAGE_BUTTON_ICON = "mdi:restart"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Eldom sensor platform."""

    eldom_data: EldomData = hass.data[DOMAIN][config_entry.entry_id]

    await eldom_data.coordinator.async_config_entry_first_refresh()

    entities_to_add = []

    for flat_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_FLAT_BOILER
    ).values():
        entities_to_add.append(
            ResetEnergyUsageButton(flat_boiler, eldom_data.coordinator)
        )

    for smart_boiler in eldom_data.coordinator.data.get(
        DEVICE_TYPE_SMART_BOILER
    ).values():
        entities_to_add.append(
            ResetEnergyUsageButton(smart_boiler, eldom_data.coordinator)
        )

    async_add_entities(entities_to_add)


class ResetEnergyUsageButton(ButtonEntity, CoordinatorEntity):
    """Button to reset energy usage for an Eldom boiler device."""

    def __init__(
        self, eldom_boiler: EldomBoiler, coordinator: EldomCoordinator
    ) -> None:
        """Initialize an Eldom energy consumption sensor."""
        super().__init__(coordinator)

        self._eldom_boiler = eldom_boiler

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this water heater."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._eldom_boiler.device_id))},
        )

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self._eldom_boiler.device_id}-reset-energy-usage-button"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self._eldom_boiler.name}'s {RESET_ENERGY_USAGE_BUTTON}"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        return RESET_ENERGY_USAGE_BUTTON_ICON

    async def async_press(self) -> None:
        """Handle the button press."""
        await self._eldom_boiler.reset_energy_usage()
